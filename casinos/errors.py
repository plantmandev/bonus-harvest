"""Named harvest errors. Raise these instead of generic exceptions so the
dashboard and newsletter can show specific remedies."""


class HarvestError(RuntimeError):
    code   = 'Unknown'
    remedy = 'Check the logs for details.'


class GmailAuthExpiredError(HarvestError):
    code   = 'GmailAuthExpired'
    remedy = 'Run: python3 auth/gmail.py'


class AccountVerificationRequired(HarvestError):
    """Raised when a casino requires manual identity verification (selfie, ID, etc.)."""
    code   = 'AccountVerification'
    remedy = 'Log into the casino and complete identity/selfie verification'
