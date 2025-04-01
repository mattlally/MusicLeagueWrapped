import os
from report_generator import generate_pdf

def main():
    """Main function to generate the Music League Wrapped PDF report."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    generate_pdf(base_path)

if __name__ == "__main__":
    main()
