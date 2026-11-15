import unittest
import time
import traceback

from django.test.runner import DiscoverRunner
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill


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


def test_case(title, expected_result):
    def decorate(test_method):
        test_method.report_title = title
        test_method.expected_result = expected_result
        return test_method
    return decorate


class ReportableAssertions:
    def report_actual_result(self, actual_result):
        self._report_actual_result = actual_result


class ReportingTextTestResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
        self._started_at = {}

    def startTest(self, test):
        self._started_at[test] = time.perf_counter()
        super().startTest(test)

    def _record(self, test, status, detail='', actual_result=None):
        started_at = self._started_at.get(test, time.perf_counter())
        method = getattr(test, test._testMethodName, None)
        outcome = {
            'PASS': 'Pass',
            'FAIL': 'Fail',
            'ERROR': 'Fail',
            'SKIP': 'Not Executed',
            'EXPECTED FAILURE': 'Fail',
            'UNEXPECTED SUCCESS': 'Fail',
        }[status]
        self.records.append({
            'test': test.id(),
            'title': getattr(method, 'report_title', test.shortDescription() or test._testMethodName),
            'expected_result': getattr(
                method,
                'expected_result',
                'The behavior documented by this test is verified.',
            ),
            'actual_result': actual_result or getattr(test, '_report_actual_result', None) or (
                'Not executed: ' + detail if status == 'SKIP'
                else (str(detail).splitlines()[0] if detail else 'Passed; expected behavior verified.')
            ),
            'status': status,
            'remark': outcome,
            'duration_seconds': time.perf_counter() - started_at,
            'details': detail,
        })

    def addSuccess(self, test):
        super().addSuccess(test)
        self._record(test, 'PASS')

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record(
            test,
            'FAIL',
            ''.join(traceback.format_exception(*err)),
            actual_result=f'Assertion failure: {err[1]}',
        )

    def addError(self, test, err):
        super().addError(test, err)
        self._record(
            test,
            'ERROR',
            ''.join(traceback.format_exception(*err)),
            actual_result=f'Execution error: {err[1]}',
        )

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._record(test, 'SKIP', reason)

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self._record(test, 'EXPECTED FAILURE', ''.join(traceback.format_exception(*err)))

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self._record(test, 'UNEXPECTED SUCCESS', 'Test unexpectedly succeeded.')


class ReportingDiscoverRunner(DiscoverRunner):
    def get_resultclass(self):
        return ReportingTextTestResult

    def run_suite(self, suite, **kwargs):
        result = super().run_suite(suite, **kwargs)
        self.test_result = result
        return result


def create_excel_report(path, suite, records, coverage_rows=None, coverage_percent=None):
    workbook = Workbook()
    workbook.properties.title = suite['title']
    workbook.properties.subject = 'Automated test execution results'
    details = workbook.active
    details.title = 'Test Cases'
    details.append(['Test Case', 'Expected Result', 'Actual Result', 'Remark'])
    for record in records:
        details.append([
            record.get('title', record['test']),
            record.get('expected_result', 'The behavior documented by this test is verified.'),
            record.get('actual_result', 'Passed; expected behavior verified.'),
            record.get('remark', 'Pass' if record['status'] == 'PASS' else 'Fail'),
        ])
    remarks = [record.get('remark', 'Pass' if record['status'] == 'PASS' else 'Fail') for record in records]
    details.append([])
    details.append(['Total', len(records), '', ''])
    details.append(['Pass', remarks.count('Pass'), '', ''])
    details.append(['Fail', remarks.count('Fail'), '', ''])
    details.append(['Not Executed', remarks.count('Not Executed'), '', ''])
    details.freeze_panes = 'A2'
    details.auto_filter.ref = f'A1:D{len(records) + 1}'
    details.column_dimensions['A'].width = 48
    details.column_dimensions['B'].width = 64
    details.column_dimensions['C'].width = 64
    details.column_dimensions['D'].width = 18
    for row in details.iter_rows(min_row=2, max_row=len(records) + 1):
        row[0].alignment = Alignment(vertical='top', wrap_text=True)
        row[1].alignment = Alignment(vertical='top', wrap_text=True)
        row[2].alignment = Alignment(vertical='top', wrap_text=True)
        remark_fill = {
            'Pass': 'C6EFCE',
            'Fail': 'FFC7CE',
            'Not Executed': 'FFEB9C',
        }.get(row[3].value)
        if remark_fill:
            row[3].fill = PatternFill('solid', fgColor=remark_fill)
    summary_start = len(records) + 3
    for row in details.iter_rows(min_row=summary_start, max_row=summary_start + 3):
        for cell in row[:2]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill('solid', fgColor='E2E8F0')

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
        for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row):
            for cell in row:
                cell.alignment = Alignment(vertical='top', wrap_text=True)
    if coverage_rows is not None:
        coverage.auto_filter.ref = coverage.dimensions
        coverage.freeze_panes = 'A2'

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
