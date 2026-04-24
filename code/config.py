"""
Institution-specific configuration for the Reference USA scraper.

Edit the two constants below to match your institution, then leave this file
alone. Everything else in the repo reads from here.
"""

# URL your institution's single-sign-on hits to terminate a session.
#
# Examples:
#   UW-Madison (Shibboleth):  "https://login.wisc.edu/logout"
#   Harvard (Shibboleth):     "https://www.pin1.harvard.edu/logout"
#   Michigan (Cosign/Shib):   "https://weblogin.umich.edu/cgi-bin/logout"
#   Generic CAS:              "https://sso.example.edu/cas/logout"
#
# Leave as "" if you're not sure — the scraper will just clear cookies and
# local storage, which is enough for most setups. Providing the URL also
# signs you out of the campus IdP in the same browser session.
SSO_LOGOUT_URL = ""

# Display name used only in the terminal banner and prompts. Purely cosmetic.
# Examples: "UW-Madison", "Harvard", "UMich". Leave as "your institution" if
# you don't want to bother.
INSTITUTION_NAME = "your institution"
