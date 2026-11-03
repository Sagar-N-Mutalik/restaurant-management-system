from pathlib import Path

import coverage
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from restaurant.reporting import (
    TEST_SUITES,
    ReportingDiscoverRunner,
    create_excel_report,
    get_coverage_rows,
)


class Command(BaseCommand):
    help = 'Run every automated test suite and create an Excel workbook for each.'

    def handle(self, *args, **options):
        reports_dir = Path(settings.BASE_DIR) / 'test_reports'
        reports_dir.mkdir(parents=True, exist_ok=True)
        coverage_run = coverage.Coverage(
            source=['restaurant'],
            omit=[
                '*/migrations/*',
                '*/management/*',
                '*/test_suites/*',
                '*/tests.py',
                '*/reporting.py',
            ],
        )
        coverage_run.start()
        suite_results = {}
        failed_suites = []

        try:
            for slug, suite in TEST_SUITES.items():
                self.stdout.write(f"Running {suite['title']}...")
                runner = ReportingDiscoverRunner(verbosity=0, interactive=False)
                try:
                    failures = runner.run_tests([f"restaurant.test_suites.{suite['module']}"])
                    result = getattr(runner, 'test_result', None)
                    records = list(result.records) if result else []
                    if not records:
                        records = [{
                            'test': suite['title'],
                            'status': 'ERROR',
                            'duration_seconds': 0,
                            'details': 'No test cases were discovered.',
                        }]
                    if failures or not result or not result.wasSuccessful() or not result.testsRun:
                        failed_suites.append(slug)
                    suite_results[slug] = records
                except Exception as error:
                    failed_suites.append(slug)
                    suite_results[slug] = [{
                        'test': suite['title'],
                        'status': 'ERROR',
                        'duration_seconds': 0,
                        'details': f'{type(error).__name__}: {error}',
                    }]
                    self.stderr.write(self.style.ERROR(f"{suite['title']} could not complete: {error}"))
        finally:
            coverage_run.stop()
            coverage_run.save()

        coverage_rows, coverage_percent = get_coverage_rows(coverage_run)
        for slug, suite in TEST_SUITES.items():
            create_excel_report(
                reports_dir / f'{slug}.xlsx',
                suite,
                suite_results.get(slug, []),
                coverage_rows if slug == 'white-box' else None,
                coverage_percent if slug == 'white-box' else None,
            )
            self.stdout.write(f"Created {reports_dir / f'{slug}.xlsx'}")

        if failed_suites:
            raise CommandError(f"Test failures in: {', '.join(failed_suites)}. Reports were still generated.")

        self.stdout.write(self.style.SUCCESS('All test suites passed and Excel reports were generated.'))
