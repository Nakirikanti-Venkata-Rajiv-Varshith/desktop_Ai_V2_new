from finance.accounting_tools.bank_statement_parser import (
    BankStatementParser
)


def main():

    parser = BankStatementParser()

    statements = parser.run()

    print(f"\nParsed {len(statements)} statement(s).\n")

    for statement in statements:

        print(statement.metadata)

        print(f"Transactions: {len(statement.transactions)}")

        print("-" * 80)


if __name__ == "__main__":
    main()