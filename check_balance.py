#!/usr/bin/env python3
"""
Quick balance check — logs in, opens the wallet, reads SC balance,
writes it to the local database, and quits. No bonus claiming.

Usage:
    python3 check_balance.py stake_us
    python3 check_balance.py fortune_coins
    python3 check_balance.py acebet_cc
"""

import sys
import time
from datetime import timedelta
from pathlib import Path

# Allow running from project root without installing the package
sys.path.insert(0, str(Path(__file__).parent))

from casinos.base import notify
from selenium.webdriver.support import expected_conditions as EC


def check_stake_us():
    from casinos.stake_us import StakeUS

    class StakeUSBalanceCheck(StakeUS):
        def _casino_key(self): return 'stake_us'

        def farm(self) -> timedelta:
            notify('Opening wallet for balance check...')
            self.click(self.WALLET)
            el = self.wait.until(EC.visibility_of_element_located(self.SC_BALANCE))
            balance = f'{el.text.strip()} SC'
            self.record_balance(balance)
            notify(f'SC balance: {balance}', 'SUCCESS')
            return timedelta(hours=0)  # don't reschedule

        def run(self):
            self._start_driver()
            try:
                self.login()
                self.farm()
            finally:
                self.driver.quit()

    StakeUSBalanceCheck().run()


CHECKERS = {
    'stake_us': check_stake_us,
}


def main():
    casino = sys.argv[1] if len(sys.argv) > 1 else 'stake_us'
    fn = CHECKERS.get(casino)
    if fn is None:
        print(f'Unknown casino "{casino}". Available: {", ".join(CHECKERS)}')
        sys.exit(1)
    notify(f'=== Balance check: {casino} ===')
    try:
        fn()
        notify('=== Done ===', 'SUCCESS')
    except Exception as e:
        notify(f'Check failed: {e}', 'ERROR')
        sys.exit(1)


if __name__ == '__main__':
    main()
