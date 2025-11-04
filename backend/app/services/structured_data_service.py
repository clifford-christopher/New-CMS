"""
Service for generating structured data using the structured_report_builder scripts
"""
import asyncio
import logging
import os
import subprocess
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Dict, Optional
from ..models.structured_data import SectionData

logger = logging.getLogger(__name__)

# Section names mapping (1-14)
SECTION_NAMES = {
    "1": "Company Information",
    "2": "Quarterly Income Statement",
    "3": "Annual Income Statement",
    "4": "Balance Sheet",
    "5": "Cash Flow Statement",
    "6": "Financial Ratios",
    "7": "Valuation Metrics",
    "8": "Shareholding Pattern",
    "9": "Stock Performance",
    "10": "Technical Analysis",
    "11": "Quality Assessment",
    "12": "Financial Trend Analysis",
    "13": "Proprietary Score",
    "14": "Peer Comparison"
}


class StructuredDataService:
    """Service for executing structured report generation and parsing sections"""

    def __init__(self):
        # Path to the structured_report_builder directory
        self.script_dir = Path(__file__).parent.parent.parent.parent / "structured_report_builder"
        self.script_path = self.script_dir / "generate_report_stdout.py"

        if not self.script_path.exists():
            logger.error(f"Script not found at {self.script_path}")
            raise FileNotFoundError(f"generate_report_stdout.py not found at {self.script_path}")

        # Thread pool for running subprocesses (cross-platform compatible)
        # Max 4 workers to avoid overwhelming the system
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def generate_sections(
        self,
        stock_id: str,
        requested_sections: List[str],
        timeout: int = 120
    ) -> List[SectionData]:
        """
        Execute the generate_full_report.py script to generate COMPLETE report (all 14 sections),
        then parse and return only the requested sections.

        This approach is more efficient:
        1. Generate the full report once (all 14 sections)
        2. Parse all sections from the complete report
        3. Filter and return only the requested sections

        Args:
            stock_id: Numeric stock ID (e.g., "399834")
            requested_sections: List of section IDs to extract (e.g., ["1", "2", "3"])
            timeout: Script execution timeout in seconds (default 60)

        Returns:
            List of SectionData objects containing parsed section content (only requested sections)

        Raises:
            asyncio.TimeoutError: If script execution exceeds timeout
            RuntimeError: If script execution fails
        """
        try:
            logger.info(f"Generating FULL structured report for stock {stock_id} (all 14 sections)")
            logger.info(f"Requested sections to extract: {requested_sections}")
            logger.info(f"Script path: {self.script_path}")
            logger.info(f"Script directory: {self.script_dir}")

            # Execute the script with timeout to generate COMPLETE report
            stdout, stderr, return_code = await self._execute_script(stock_id, timeout)

            # Log execution results for debugging
            logger.info(f"Script execution completed with return code: {return_code}")
            logger.info(f"Stdout length: {len(stdout)} characters")
            logger.info(f"Stderr length: {len(stderr)} characters")

            if stderr:
                logger.warning(f"Script stderr output: {stderr[:500]}")  # Log first 500 chars

            if return_code != 0:
                error_msg = f"Script execution failed with return code {return_code}. Stderr: {stderr if stderr else '(empty)'}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            # Parse ALL sections from the complete report
            all_sections = self._parse_sections(stdout, requested_sections=[str(i) for i in range(1, 15)])
            logger.info(f"Parsed {len(all_sections)} sections from complete report")

            # Filter to return only requested sections
            filtered_sections = [section for section in all_sections if section.section_id in requested_sections]
            logger.info(f"Filtered to {len(filtered_sections)} requested sections: {requested_sections}")

            if len(filtered_sections) != len(requested_sections):
                found_ids = [s.section_id for s in filtered_sections]
                missing_ids = set(requested_sections) - set(found_ids)
                logger.warning(f"Some requested sections were not found in report: {missing_ids}")

            logger.info(f"Successfully generated and filtered {len(filtered_sections)} sections for stock {stock_id}")
            return filtered_sections

        except asyncio.TimeoutError as e:
            error_msg = f"Script execution timed out after {timeout} seconds for stock {stock_id}"
            logger.error(error_msg)
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise RuntimeError(error_msg) from e
        except RuntimeError:
            # Re-raise RuntimeError as-is (already has good error message)
            raise
        except Exception as e:
            # Capture full exception details
            exception_type = type(e).__name__
            exception_msg = str(e) if str(e) else "(empty exception message)"
            error_msg = f"Failed to generate structured data for stock {stock_id}: {exception_type}: {exception_msg}"

            logger.error(error_msg)
            logger.error(f"Traceback: {traceback.format_exc()}")

            # Re-raise with descriptive message
            raise RuntimeError(error_msg) from e

    def _run_subprocess_sync(self, stock_id: str, timeout: int) -> dict:
        """
        Run subprocess synchronously using subprocess.run (cross-platform compatible).
        This method is designed to be run in a thread pool.

        Args:
            stock_id: Numeric stock ID
            timeout: Execution timeout in seconds

        Returns:
            dict with stdout, stderr, return_code, success flag
        """
        try:
            # Construct command using sys.executable for current Python interpreter
            command = [sys.executable, str(self.script_path), stock_id]

            logger.info(f"Executing command: {' '.join(command)}")
            logger.info(f"Working directory: {self.script_dir}")

            # Run subprocess with timeout
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.script_dir),
                shell=False,  # Don't use shell for security
                encoding='utf-8',
                errors='replace'  # Replace invalid characters
            )

            logger.info(f"Script completed with return code: {result.returncode}")

            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'success': result.returncode == 0
            }

        except subprocess.TimeoutExpired as e:
            logger.error(f"Script execution timed out after {timeout} seconds")
            return {
                'stdout': e.stdout if e.stdout else '',
                'stderr': e.stderr if e.stderr else '',
                'return_code': -1,
                'success': False,
                'timeout': True
            }

        except FileNotFoundError as e:
            error_msg = f"Python executable or script not found: {e}"
            logger.error(error_msg)
            return {
                'stdout': '',
                'stderr': error_msg,
                'return_code': -1,
                'success': False
            }

        except Exception as e:
            exception_type = type(e).__name__
            exception_msg = str(e) if str(e) else "(empty exception message)"
            error_msg = f"Subprocess execution failed: {exception_type}: {exception_msg}"
            logger.error(error_msg)
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'stdout': '',
                'stderr': error_msg,
                'return_code': -1,
                'success': False
            }

    async def _execute_script(self, stock_id: str, timeout: int) -> tuple[str, str, int]:
        """
        Execute the generate_full_report.py script via subprocess in thread pool.
        This is cross-platform compatible (Windows, Linux, Mac).

        Args:
            stock_id: Numeric stock ID
            timeout: Execution timeout in seconds

        Returns:
            Tuple of (stdout, stderr, return_code)
        """
        try:
            # Log execution details
            logger.info(f"Executing script: python {self.script_path} {stock_id}")
            logger.info(f"Working directory: {self.script_dir}")
            logger.info(f"Timeout: {timeout} seconds")

            # Run subprocess.run() in thread pool to avoid blocking event loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._run_subprocess_sync,
                stock_id,
                timeout
            )

            # Check if execution was successful
            if result.get('timeout'):
                raise asyncio.TimeoutError(f"Script execution timed out after {timeout} seconds")

            if not result['success'] and result['return_code'] == -1:
                # Error during subprocess execution (not script error)
                raise RuntimeError(result['stderr'])

            return result['stdout'], result['stderr'], result['return_code']

        except asyncio.TimeoutError:
            logger.error(f"Script execution timed out after {timeout} seconds")
            raise
        except RuntimeError:
            # Re-raise RuntimeError as-is
            raise
        except Exception as e:
            exception_type = type(e).__name__
            exception_msg = str(e) if str(e) else "(empty exception message)"
            error_msg = f"Subprocess execution failed: {exception_type}: {exception_msg}"
            logger.error(error_msg)
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise RuntimeError(error_msg) from e

    def _parse_sections(self, output: str, requested_sections: List[str]) -> List[SectionData]:
        """
        Parse sections from script output using 80 '=' separator and validate with section headers

        Args:
            output: Raw script output
            requested_sections: List of section IDs to extract

        Returns:
            List of SectionData objects
        """
        import re

        sections_data = []

        # Split by section separator (80 '=' characters)
        section_separator = "=" * 80
        raw_sections = output.split(section_separator)

        # Skip the first element (before first separator)
        raw_sections = raw_sections[1:] if len(raw_sections) > 1 else []

        logger.info(f"Found {len(raw_sections)} raw sections split by separator")

        # Group consecutive sections: header section + following content sections
        i = 0
        while i < len(raw_sections):
            content = raw_sections[i].strip()

            # Skip empty sections
            if not content:
                i += 1
                continue

            # Extract section number and name from "SECTION X: NAME" header
            # Pattern matches: "SECTION 1: Company Information" or "SECTION 10: Technical Analysis"
            match = re.search(r'SECTION\s+(\d+):\s*(.+?)(?:\n|$)', content, re.MULTILINE)

            if not match:
                # No valid section header found, skip this section
                logger.warning(f"Skipping section without valid header. Content preview: {content[:100]}")
                i += 1
                continue

            section_id = match.group(1)
            section_name_from_header = match.group(2).strip()

            # Collect full section content by combining this piece with the next piece(s) until we hit another section header
            full_content = content
            j = i + 1

            # Look ahead to collect content pieces that don't have section headers
            while j < len(raw_sections):
                next_content = raw_sections[j].strip()
                if not next_content:
                    j += 1
                    continue

                # Check if next piece has a section header
                next_match = re.search(r'SECTION\s+(\d+):\s*(.+?)(?:\n|$)', next_content, re.MULTILINE)
                if next_match:
                    # Hit another section header, stop collecting
                    break

                # This is continuation content, add it to full_content
                full_content += "\n\n" + section_separator + "\n\n" + next_content
                j += 1

            # Move index past all collected content
            i = j

            # Only include if this section was requested
            if section_id not in requested_sections:
                logger.debug(f"Skipping section {section_id} (not requested)")
                continue

            # Validate against expected section names
            expected_name = SECTION_NAMES.get(section_id)
            if expected_name:
                # Log if section name doesn't match expected (for monitoring)
                if expected_name.lower() != section_name_from_header.lower():
                    logger.warning(
                        f"Section {section_id} name mismatch: "
                        f"expected '{expected_name}', got '{section_name_from_header}'"
                    )
                # Use the name from the header (actual output)
                section_name = section_name_from_header
            else:
                # Unknown section ID
                logger.warning(f"Unknown section ID: {section_id}")
                section_name = section_name_from_header

            # Create SectionData object with full content
            sections_data.append(SectionData(
                section_id=section_id,
                section_name=section_name,
                content=full_content
            ))

            logger.info(f"Successfully parsed Section {section_id}: {section_name} ({len(full_content)} characters)")

        logger.info(f"Parsed {len(sections_data)} requested sections out of {len(raw_sections)} total sections")

        return sections_data

    def reorder_sections(
        self,
        sections: List[SectionData],
        order: List[str]
    ) -> List[SectionData]:
        """
        Reorder sections based on provided order list

        Args:
            sections: List of SectionData objects
            order: Desired order of section IDs

        Returns:
            Reordered list of SectionData objects
        """
        # Create a mapping of section_id to SectionData
        section_map = {section.section_id: section for section in sections}

        # Reorder based on provided order
        reordered = []
        for section_id in order:
            if section_id in section_map:
                reordered.append(section_map[section_id])

        logger.info(f"Reordered {len(reordered)} sections")

        return reordered
