import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

from data_logger import ExcelStore, MoringaApplication, SensorError, Settings, analyze_bands, make_handler, parse_sensor_payload


class FakeSensor:
    def scan(self):
        return {"R": 95.67, "S": 68.5, "T": 9.27, "U": 115.13, "V": 122.46, "W": 116.36}


class SensorParsingTests(unittest.TestCase):
    def test_parses_text_payload(self):
        values = parse_sensor_payload("R,1 S,2\nT,3 U,4 V,5 W,6")
        self.assertEqual(values, {"R": 1.0, "S": 2.0, "T": 3.0, "U": 4.0, "V": 5.0, "W": 6.0})

    def test_parses_json_payload_case_insensitively(self):
        values = parse_sensor_payload('{"r": 1, "s": 2, "t": 3, "u": 4, "v": 5, "w": 6}')
        self.assertEqual(values["W"], 6.0)

    def test_rejects_incomplete_payload(self):
        with self.assertRaises(SensorError):
            parse_sensor_payload("R,1 S,2")


class AnalysisTests(unittest.TestCase):
    def test_lpqi_uses_red_edge_and_nir_averages(self):
        result = analyze_bands({"R": 99, "S": 20, "T": 40, "U": 60, "V": 90, "W": 120})
        self.assertAlmostEqual(result["red_edge_average"], 30)
        self.assertAlmostEqual(result["nir_average"], 90)
        self.assertAlmostEqual(result["lpqi"], 0.5)
        self.assertEqual(result["quality"], "Good")

    def test_zero_denominator_is_rejected(self):
        with self.assertRaises(SensorError):
            analyze_bands({band: 0 for band in "RSTUVW"})


class ApplicationTests(unittest.TestCase):
    def test_scan_is_analyzed_persisted_and_returned(self):
        with tempfile.TemporaryDirectory() as directory:
            workbook = Path(directory) / "sensor_data.xlsx"
            settings = Settings("http://sensor/scan", workbook)
            app = MoringaApplication(settings, sensor=FakeSensor())
            result = app.scan()
            self.assertTrue(result["ok"])
            self.assertEqual(result["sample_no"], 1)
            self.assertEqual(result["quality"], "Good")
            self.assertEqual(len(app.store.history()), 1)

            reloaded = ExcelStore(workbook)
            self.assertAlmostEqual(reloaded.history()[0]["lpqi"], result["lpqi"])

    def test_http_scan_status_and_history_use_persisted_record(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = Settings(
                "http://sensor/scan",
                Path(directory) / "sensor_data.xlsx",
                web_root=Path(directory),
            )
            app = MoringaApplication(settings, sensor=FakeSensor())
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base_url = f"http://127.0.0.1:{server.server_port}"
            try:
                request = Request(base_url + "/api/scan", method="POST")
                with urlopen(request, timeout=2) as response:
                    scan = json.load(response)
                with urlopen(base_url + "/api/history", timeout=2) as response:
                    history = json.load(response)
                with urlopen(base_url + "/api/status", timeout=2) as response:
                    status = json.load(response)
                self.assertEqual(history["rows"][0]["sample_no"], scan["sample_no"])
                self.assertAlmostEqual(history["rows"][0]["lpqi"], scan["lpqi"])
                self.assertEqual(status["samples"], 1)
                self.assertTrue(status["last_scan_ok"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
