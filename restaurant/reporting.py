import unittest
import time
import traceback
from datetime import datetime

from django.test.runner import DiscoverRunner
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


TEST_SUITES = {
    'unit': {
        'title': 'Unit testing',
        'description': 'Checks individual pricing and menu customization components.',
        'module': 'test_unit',
    },
    'integration': {
        'title': 'Integration testing',
        'description': 'Checks order processing, persistence, and payment workflows together.',
        'module': 'test_integration',
    },
    'black-box': {
        'title': 'Black-box testing',
        'description': 'Checks public HTTP routes and API behavior without relying on internals.',
        'module': 'test_black_box',
    },
    'white-box': {
        'title': 'White-box testing',
        'description': 'Checks internal branches and reports application source-code coverage.',
        'module': 'test_white_box',
    },
    'smoke': {
        'title': 'Smoke testing',
        'description': 'Checks that the main website pages and workflows respond successfully.',
        'module': 'test_smoke',
    },
    'regression': {
        'title': 'Regression testing',
        'description': 'Checks key order and payment behavior against regressions.',
        'module': 'test_regression',
    },
    'performance': {
        'title': 'Performance testing',
        'description': 'Runs bounded response-time and pricing-operation checks.',
        'module': 'test_performance',
    },
}


class ReportingTextTestResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
        self._started_at = {}

    def startTest(self, test):
        self._started_at[test] = time.perf_counter()
        super().startTest(test)

    def _record(self, test, status, detail=''):
        started_at = self._started_at.get(test, time.perf_counter())
        self.records.append({
            'test': test.id(),
            'status': status,
            'duration_seconds': time.perf_counter() - started_at,
            'details': detail,
        })

    def addSuccess(self, test):
        super().addSuccess(test)
        self._record(test, 'PASS')

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record(test, 'FAIL', ''.join(traceback.format_exception(*err)))

    def addError(self, test, err):
        super().addError(test, err)
        self._record(test, 'ERROR', ''.join(traceback.format_exception(*err)))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._record(test, 'SKIP', reason)

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self._record(test, 'EXPECTED FAILURE', ''.join(traceback.format_exception(*err)))

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self._record(test, 'UNEXPECTED SUCCESS')


class ReportingDiscoverRunner(DiscoverRunner):
    def get_resultclass(self):
        return ReportingTextTestResult

    def run_suite(self, suite, **kwargs):
        result = super().run_suite(suite, **kwargs)
        self.test_result = result
        return result


def create_excel_report(path, suite, records, coverage_rows=None, coverage_percent=None):
    workbook = Workbook()
    summary = workbook.active
    summary.title = 'Summary'

    statuses = [record['status'] for record in records]
    duration = sum(record.get('duration_seconds', 0) for record in records)
    summary.append(['Test suite', suite['title']])
    summary.append(['Generated at', datetime.now().astimezone().isoformat(timespec='seconds')])
    summary.append(['Result', 'PASS' if records and all(status in ('PASS', 'SKIP', 'EXPECTED FAILURE') for status in statuses) else 'FAIL'])
    summary.append(['Tests run', len(records)])
    summary.append(['Passed', statuses.count('PASS')])
    summary.append(['Failed', statuses.count('FAIL')])
    summary.append(['Errors', statuses.count('ERROR')])
    summary.append(['Skipped', statuses.count('SKIP')])
    summary.append(['Duration (seconds)', round(duration, 3)])
    if coverage_percent is not None:
        summary.append(['Application coverage (%)', round(coverage_percent, 2)])
    summary.column_dimensions['A'].width = 28
    summary.column_dimensions['B'].width = 40

    details = workbook.create_sheet('Test cases')
    details.append(['Test', 'Status', 'Duration (seconds)', 'Details'])
    for record in records:
        details.append([
            record['test'],
            record['status'],
            round(record.get('duration_seconds', 0), 4),
            record.get('details', ''),
        ])
    details.freeze_panes = 'A2'
    details.auto_filter.ref = details.dimensions

    if coverage_rows is not None:
        coverage = workbook.create_sheet('Source coverage')
        coverage.append(['Source file', 'Statements', 'Covered', 'Missing', 'Coverage (%)'])
        coverage.append(['TOTAL', sum(row[1] for row in coverage_rows), sum(row[2] for row in coverage_rows),
                         sum(row[3] for row in coverage_rows), round(coverage_percent or 0, 2)])
        for row in coverage_rows:
            coverage.append(row)
        coverage.freeze_panes = 'A2'
        coverage.auto_filter.ref = coverage.dimensions

    for sheet in workbook.worksheets:
        for cell in sheet[1]:
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = PatternFill('solid', fgColor='334155')
            cell.alignment = Alignment(vertical='top')
        for column in sheet.columns:
            width = min(max(max(len(str(cell.value or '')) for cell in column) + 2, 12), 72)
            sheet.column_dimensions[get_column_letter(column[0].column)].width = width
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(vertical='top', wrap_text=True)

    path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(path)


def get_coverage_rows(coverage):
    rows = []
    total_statements = 0
    total_covered = 0
    for filename in sorted(coverage.get_data().measured_files()):
        _, statements, _, missing, _ = coverage.analysis2(filename)
        statement_count = len(statements)
        covered_count = statement_count - len(missing)
        if not statement_count:
            continue
        total_statements += statement_count
        total_covered += covered_count
        rows.append([
            filename,
            statement_count,
            covered_count,
            len(missing),
            round(covered_count * 100 / statement_count, 2),
        ])
    percent = total_covered * 100 / total_statements if total_statements else 0
    return rows, percent
