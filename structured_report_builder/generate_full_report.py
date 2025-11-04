#!/usr/bin/env python3
"""
Comprehensive Stock Report Generator
Generates a complete stock analysis report with all 14 sections
Usage: python generate_full_report.py <stock_id> [exchange]
"""

import sys
import argparse
from datetime import datetime
import traceback

# Import all section builders
from section1_builder import Section1Builder
from section2_builder import Section2Builder
from section3_builder import Section3Builder
from section4_builder import Section4Builder
from section5_builder import Section5Builder
from section6_builder import Section6Builder
from section7_builder import Section7Builder
from section8_builder import Section8Builder
from section9_builder import Section9Builder
from section10_builder import Section10Builder
from section11_builder import Section11Builder
from section12_builder import Section12Builder
from section13_builder import Section13Builder
from section14_builder_fixed import Section14Builder

def generate_separator():
    """Generate section separator"""
    return "\n" + "="*80 + "\n"

def generate_full_report(stock_id, exchange=0):
    """
    Generate complete stock report with all 14 sections

    Args:
        stock_id (int): Stock ID
        exchange (int): Exchange ID (default 0)

    Returns:
        str: Complete formatted report
    """
    report = []
    errors = []
    main_header_fallback = None  # Store main_header for sharing between sections

    print(f"Starting report generation for Stock ID: {stock_id}, Exchange: {exchange}")
    print("-" * 60)

    # Section 1: Stock Overview
    try:
        print("Building Section 1: Stock Overview...")
        builder = Section1Builder(stock_id, exchange)
        content = builder.build_section()
        if content:
            report.append(content)
            # Get main_header for other sections to use as fallback
            main_header_fallback = builder.get_main_header()
            if main_header_fallback:
                print(f"  [INFO] Main header available for fallback: {main_header_fallback.get('stock_name', 'Unknown')}")
        else:
            errors.append("Section 1: No content generated")
            print("  Warning: No content for Section 1")
    except Exception as e:
        errors.append(f"Section 1: {str(e)}")
        print(f"  Error in Section 1: {str(e)}")

    # Section 2: Investment Rating Summary
    try:
        print("Building Section 2: Investment Rating Summary...")
        builder = Section2Builder(stock_id, exchange)
        content = builder.build_section()
        if content:
            report.append(generate_separator())
            report.append(content)
        else:
            errors.append("Section 2: No content generated")
            print("  Warning: No content for Section 2")
    except Exception as e:
        errors.append(f"Section 2: {str(e)}")
        print(f"  Error in Section 2: {str(e)}")

    # Section 3: Stock Performance Analysis
    try:
        print("Building Section 3: Stock Performance Analysis...")
        builder = Section3Builder(stock_id, exchange)
        content = builder.build_section()
        if content:
            report.append(generate_separator())
            report.append(content)
        else:
            errors.append("Section 3: No content generated")
            print("  Warning: No content for Section 3")
    except Exception as e:
        errors.append(f"Section 3: {str(e)}")
        print(f"  Error in Section 3: {str(e)}")

    # Section 4: Price Targets & Recommendations
    try:
        print("Building Section 4: Price Targets & Recommendations...")
        builder = Section4Builder(stock_id, exchange)
        content = builder.build_section()
        if content:
            report.append(generate_separator())
            report.append(content)
        else:
            errors.append("Section 4: No content generated")
            print("  Warning: No content for Section 4")
    except Exception as e:
        errors.append(f"Section 4: {str(e)}")
        print(f"  Error in Section 4: {str(e)}")

    # Section 5: Institutional Activity
    try:
        print("Building Section 5: Institutional Activity...")
        builder = Section5Builder(stock_id, exchange)
        content = builder.build_section()
        if content:
            report.append(generate_separator())
            report.append(content)
        else:
            errors.append("Section 5: No content generated")
            print("  Warning: No content for Section 5")
    except Exception as e:
        errors.append(f"Section 5: {str(e)}")
        print(f"  Error in Section 5: {str(e)}")

    # Section 6: Key Financials
    try:
        print("Building Section 6: Key Financials...")
        builder = Section6Builder(stock_id, exchange)
        content = builder.build_section()
        if content:
            report.append(generate_separator())
            report.append(content)
        else:
            errors.append("Section 6: No content generated")
            print("  Warning: No content for Section 6")
    except Exception as e:
        errors.append(f"Section 6: {str(e)}")
        print(f"  Error in Section 6: {str(e)}")

    # Section 7: Valuation Analysis (with MongoDB)
    try:
        print("Building Section 7: Valuation Analysis...")
        builder = Section7Builder(stock_id, exchange, use_mongodb=True)
        content = builder.build_section()
        if content:
            report.append(generate_separator())
            report.append(content)
        else:
            errors.append("Section 7: No content generated")
            print("  Warning: No content for Section 7")
    except Exception as e:
        errors.append(f"Section 7: {str(e)}")
        print(f"  Error in Section 7: {str(e)}")

    # Section 8: Growth Metrics
    try:
        print("Building Section 8: Growth Metrics...")
        builder = Section8Builder(stock_id, exchange)
        content = builder.build_section()
        if content:
            report.append(generate_separator())
            report.append(content)
        else:
            errors.append("Section 8: No content generated")
            print("  Warning: No content for Section 8")
    except Exception as e:
        errors.append(f"Section 8: {str(e)}")
        print(f"  Error in Section 8: {str(e)}")

    # Section 9: Risk Analysis
    try:
        print("Building Section 9: Risk Analysis...")
        builder = Section9Builder(stock_id, exchange)
        content = builder.build_section()
        if content:
            report.append(generate_separator())
            report.append(content)
        else:
            errors.append("Section 9: No content generated")
            print("  Warning: No content for Section 9")
    except Exception as e:
        errors.append(f"Section 9: {str(e)}")
        print(f"  Error in Section 9: {str(e)}")

    # Section 10: Technical Analysis (with MongoDB)
    try:
        print("Building Section 10: Technical Analysis...")
        builder = Section10Builder(stock_id, exchange, use_mongodb=True)
        content = builder.build_section()
        if content:
            report.append(generate_separator())
            report.append(content)
        else:
            errors.append("Section 10: No content generated")
            print("  Warning: No content for Section 10")
    except Exception as e:
        errors.append(f"Section 10: {str(e)}")
        print(f"  Error in Section 10: {str(e)}")

    # Section 11: Quality Assessment (with MongoDB)
    try:
        print("Building Section 11: Quality Assessment...")
        builder = Section11Builder(stock_id, exchange, use_mongodb=True)
        content = builder.build_section()
        if content:
            report.append(generate_separator())
            report.append(content)
        else:
            errors.append("Section 11: No content generated")
            print("  Warning: No content for Section 11")
    except Exception as e:
        errors.append(f"Section 11: {str(e)}")
        print(f"  Error in Section 11: {str(e)}")

    # Section 12: Financial Trend Analysis (with MongoDB)
    try:
        print("Building Section 12: Financial Trend Analysis...")
        builder = Section12Builder(stock_id, exchange, use_mongodb=True)
        content = builder.build_section()
        if content:
            report.append(generate_separator())
            report.append(content)
        else:
            errors.append("Section 12: No content generated")
            print("  Warning: No content for Section 12")
    except Exception as e:
        errors.append(f"Section 12: {str(e)}")
        print(f"  Error in Section 12: {str(e)}")

    # Section 13: Proprietary Score & Advisory (with MongoDB)
    try:
        print("Building Section 13: Proprietary Score & Advisory...")
        builder = Section13Builder(stock_id, exchange, use_mongodb=True)
        content = builder.build_section()
        if content:
            report.append(generate_separator())
            report.append(content)
        else:
            errors.append("Section 13: No content generated")
            print("  Warning: No content for Section 13")
    except Exception as e:
        errors.append(f"Section 13: {str(e)}")
        print(f"  Error in Section 13: {str(e)}")

    # Section 14: Peer Comparison
    try:
        print("Building Section 14: Peer Comparison...")
        builder = Section14Builder(stock_id, exchange)
        content = builder.build_section()
        if content:
            report.append(generate_separator())
            report.append(content)
        else:
            errors.append("Section 14: No content generated")
            print("  Warning: No content for Section 14")
    except Exception as e:
        errors.append(f"Section 14: {str(e)}")
        print(f"  Error in Section 14: {str(e)}")

    # Add footer
    report.append(generate_separator())
    report.append(f"\nReport generated on: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}")

    # Add error summary if any
    if errors:
        report.append("\n\nERRORS/WARNINGS:")
        report.append("-" * 40)
        for error in errors:
            report.append(f"- {error}")

    print("-" * 60)
    print(f"Success: Report generation completed with {len(errors)} errors/warnings")

    return "\n".join(report)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate comprehensive stock analysis report',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_full_report.py 513374          # TCS with default exchange
  python generate_full_report.py 399834 0        # Infosys with exchange 0
  python generate_full_report.py 291436 --exchange 0  # Bank of Maharashtra
        """
    )

    parser.add_argument('stock_id', type=int, help='Stock ID (e.g., 513374 for TCS)')
    parser.add_argument('exchange', type=int, nargs='?', default=0,
                       help='Exchange ID (default: 0)')
    parser.add_argument('--output', '-o', type=str,
                       help='Output file name (default: stock_report_<id>_<date>.txt)')
    parser.add_argument('--print', '-p', action='store_true',
                       help='Also print report to console')

    args = parser.parse_args()

    # Generate output filename if not provided
    if args.output:
        output_file = args.output
    else:
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"stock_report_{args.stock_id}_{date_str}.txt"

    try:
        print(f"\n{'='*60}")
        print(f"STOCK REPORT GENERATOR")
        print(f"{'='*60}")
        print(f"Stock ID: {args.stock_id}")
        print(f"Exchange: {args.exchange}")
        print(f"Output file: {output_file}")
        print(f"{'='*60}\n")

        # Generate report
        report = generate_full_report(args.stock_id, args.exchange)

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\nSuccess: Report saved to: {output_file}")
        print(f"  File size: {len(report):,} characters")

        # Print to console if requested
        if args.print:
            print("\n" + "="*60)
            print("FULL REPORT CONTENT:")
            print("="*60)
            print(report)

    except KeyboardInterrupt:
        print("\n\nError: Report generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: Fatal error: {str(e)}")
        print("\nDetailed traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()