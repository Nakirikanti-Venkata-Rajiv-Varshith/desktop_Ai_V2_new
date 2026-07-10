import json
from pathlib import Path
import re
import fitz
import pdfplumber
from pypdf import PdfReader

from config.settings import DATA_DIR
from models.accounting.bank_statement import (
    BankStatement,
    StatementMetadata
)
from models.accounting.parsed_header import (
    ParsedHeader
)

from models.accounting.bank_transaction import (
    BankTransaction
)

class BankStatementParser:

    PDF_DIRECTORY = (
        Path(DATA_DIR)
        / "finance_data"
        / "bank_statements"
    )

    OUTPUT_FILE = (
        Path(DATA_DIR)
        / "finance_data"
        / "bank_transactions.json"
    )

    BANK_STATEMENTS = {

        "Union_bank_1.pdf": {

            "password": "NAKI0407",

            "bank_name": "Union Bank of India"

        }

    }

    EXTRACTORS = (

        "_extract_using_pdfplumber",

        "_extract_using_pymupdf",

        "_extract_using_pypdf"

    )

    
    def __init__(
        self
    ):
        """
        Bank Statement Parser.
        """

    def run(
        self
    ) -> list:
        """
        Parse every bank statement found in the
        configured directory.

        Workflow

        Find PDFs
            ↓
        Extract PDF Text
            ↓
        Parse Transactions
            ↓
        Save Transactions
        """

        statements = []

        for pdf_path in self._find_bank_statements():

            statement = self._process_statement(
                pdf_path
            )

            if statement is None:
                continue

            self._save_transactions(
                statement
            )

            statements.append(
                statement
            )

        return statements


    def _find_bank_statements(
        self
    ) -> list[Path]:
        """
        Locate every PDF bank statement inside the
        configured directory.
        """

        self.PDF_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True
        )

        return sorted(
            self.PDF_DIRECTORY.glob("*.pdf")
        )

    def _process_statement(
        self,
        pdf_path: Path
    ):
        """
        Process a single bank statement.

        PDF
            ↓
        Extract Text
            ↓
        Parse Transactions
            ↓
        BankStatement
        """

        config = self.BANK_STATEMENTS.get(
            pdf_path.name,
            {}
        )

        password = config.get(
            "password"
        )

        pdf_text = self._extract_pdf_text(
            pdf_path,
            password
        )

        statement = self._parse_transactions(
            pdf_text=pdf_text,
            statement_file=pdf_path.name
        )

        return statement


    def _extract_pdf_text(
        self,
        pdf_path: Path,
        password: str | None = None
    ) -> str:
        """
        Extract PDF text using multiple fallback
        extraction engines.
        """

        last_error = None

        for extractor_name in self.EXTRACTORS:

            extractor = getattr(
                self,
                extractor_name
            )

            try:

                text = extractor(
                    pdf_path,
                    password
                )

                if text.strip():
                    return text

            except Exception as e:

                last_error = e

        raise RuntimeError(
            f"Unable to extract text from '{pdf_path.name}'."
        ) from last_error


    def _extract_using_pdfplumber(
        self,
        pdf_path: Path,
        password: str | None = None
    ) -> str:
        """
        Primary extraction strategy using pdfplumber.
        """

        pages = []

        with pdfplumber.open(
            pdf_path,
            password=password
        ) as pdf:

            for page in pdf.pages:

                text = page.extract_text()

                if text:
                    pages.append(text)

        return "\n\n".join(pages)


    def _extract_using_pymupdf(
        self,
        pdf_path: Path,
        password: str | None = None
    ) -> str:
        """
        Secondary extraction strategy using
        PyMuPDF.
        """

        document = fitz.open(
            pdf_path
        )

        try:

            if document.is_encrypted:

                if password:

                    if not document.authenticate(
                        password
                    ):
                        raise RuntimeError(
                            "Invalid PDF password."
                        )

                else:

                    raise RuntimeError(
                        "PDF is password protected."
                    )

            pages = []

            for page in document:

                pages.append(
                    page.get_text()
                )

            return "\n\n".join(
                pages
            )

        finally:

            document.close()


    def _extract_using_pypdf(
        self,
        pdf_path: Path,
        password: str | None = None
    ) -> str:
        """
        Final extraction fallback using pypdf.
        """

        reader = PdfReader(
            str(pdf_path)
        )

        if reader.is_encrypted:

            if password:

                reader.decrypt(
                    password
                )

            else:

                raise RuntimeError(
                    "PDF is password protected."
                )

        pages = []

        for page in reader.pages:

            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n\n".join(
            pages
            )

    def _parse_statement_period(
        self,
        pdf_text: str
    ) -> tuple[str | None, str | None]:
        """
        Extract the statement period from the
        bank statement.
        """

        pattern = re.compile(
            r"STATEMENT OF ACCOUNT FOR THE PERIOD FROM\s+(\d{2}-\d{2}-\d{4})\s+TO\s+(\d{2}-\d{2}-\d{4})",
            re.IGNORECASE
        )

        match = pattern.search(
            pdf_text
        )

        if match:

            return (
                match.group(1),
                match.group(2)
            )

        return (
            None,
            None
        )

    def _parse_transactions(
        self,
        pdf_text: str,
        statement_file: str
    ) -> BankStatement:
        """
        Parse the extracted PDF text into a
        structured BankStatement.
        """

        config = self.BANK_STATEMENTS.get(statement_file, {})

        period_from, period_to = self._parse_statement_period(
            pdf_text
        )

        metadata = StatementMetadata(

            bank_name=config.get(
                "bank_name",
                "Unknown"
            ),

            statement_file=statement_file,

            statement_period_from=period_from,

            statement_period_to=period_to

        )

        transaction_blocks = self._split_transaction_blocks(
            pdf_text
        )

        transactions = []

        for block in transaction_blocks:

            transaction = self._parse_transaction_block(
                block
            )

            if transaction is not None:

                transactions.append(
                    transaction
                )

        return BankStatement(
            metadata=metadata,
            transactions=transactions
        )

    def _split_transaction_blocks(
        self,
        pdf_text: str
    ) -> list[list[str]]:
        """
        Split the statement into transaction blocks.

        Each block is returned as a list of lines.
        """

        lines = pdf_text.splitlines()

        blocks = []

        current_block = []

        pattern = re.compile(
            r"^\d+\s+\d{2}-\d{2}-\d{4}"
        )

        stop_markers = (

            "Total Debits",

            "Summary",

            "LINKED CASA ACCOUNTS",

            "LINKED DEPOSITS",

            "LINKED LOAN",

            "LINKED LOCKERS",

            "OTHER DIGITAL PRODUCTS"

        )

        for line in lines:

            line = line.strip()

            if not line:
                continue

            if any(
                marker in line
                for marker in stop_markers
            ):
                break

            if pattern.match(line):

                if current_block:

                    blocks.append(
                        current_block
                    )

                current_block = [line]

            else:

                if current_block:

                    current_block.append(
                        line
                    )

        if current_block:

            blocks.append(
                current_block
            )

        print("\n")
        print("=" * 80)
        print(f"FOUND {len(blocks)} TRANSACTION BLOCKS")
        print("=" * 80)

        return blocks

    def _parse_header(
        self,
        header: str
    ) -> ParsedHeader:
        """
        Parse the first line of a transaction.

        Supports both formats:

        1 01-06-2026 10.00 418.04 Cr

        and

        22 12-06-2026 UPIAR/... 450.00 771.04 Cr
        """

        tokens = header.split()

        if len(tokens) < 5:

            raise ValueError(
                f"Invalid transaction header:\n{header}"
            )

        transaction_number = int(
            tokens[0]
        )

        date = tokens[1]

        entry_type = tokens[-1].upper()

        balance = float(
            tokens[-2].replace(",", "")
        )

        amount = float(
            tokens[-3].replace(",", "")
        )

        header_description = " ".join(
            tokens[2:-3]
        ).strip()

        return ParsedHeader(

            transaction_number=transaction_number,

            date=date,

            header_description=header_description,

            amount=amount,

            balance=balance,

            entry_type=entry_type

        )

    def _parse_description(
        self,
        lines: list[str]
    ):
        """
        Merge description lines into one string.
        """

        return " ".join(lines).strip()

    def _parse_transaction_block(
        self,
        block: list[str]
    ) -> BankTransaction:
        """
        Parse a transaction block into a
        BankTransaction.
        """

        header = self._parse_header(
            block[0]
        )

        description = " ".join(

            filter(

                None,

                [

                    header.header_description,

                    self._parse_description(
                        block[1:]
                    )

                ]

            )

        ).strip()

        return BankTransaction(

            transaction_number=header.transaction_number,

            date=header.date,

            description=description,

            amount=header.amount,

            transaction_type=header.entry_type,

            balance=header.balance,

            raw_text="\n".join(block)

        )


    def _save_transactions(
        self,
        statement: BankStatement
    ):
        """
        Save parsed statements.
        """

        self.OUTPUT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        data = {
            "statements": []
        }

        if self.OUTPUT_FILE.exists():

            try:

                with open(
                    self.OUTPUT_FILE,
                    "r",
                    encoding="utf-8"
                ) as f:

                    data = json.load(f)

            except Exception:

                pass

        data.setdefault(
            "statements",
            []
        )

        data["statements"] = [

            existing

            for existing in data["statements"]

            if existing["metadata"]["statement_file"]
            != statement.metadata.statement_file

        ]

        data["statements"].append(

            statement.model_dump(
                mode="json",
                exclude_none=True
            )

        )

        with open(
            self.OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )