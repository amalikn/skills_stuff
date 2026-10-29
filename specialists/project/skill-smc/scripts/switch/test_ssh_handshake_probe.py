"""Offline checks for ssh_handshake_probe.py: parsing an old and a new switch's handshake, and splitting one session's output.

Run: python3 -m unittest test_ssh_handshake_probe (from scripts/switch/). No network.
"""

import unittest

import ssh_handshake_probe as p

OLD = """debug1: Remote protocol version 1.99, remote software version IPSSH-6.6.0
debug1: kex: algorithm: diffie-hellman-group1-sha1
debug1: kex: host key algorithm: ssh-dss
debug1: kex: server->client cipher: aes128-cbc MAC: hmac-md5 compression: none
debug1: Authentications that can continue: publickey,password
"""
NEW = """debug1: Remote protocol version 2.0, remote software version TPSSH-1.0.0
debug1: kex: algorithm: diffie-hellman-group16-sha512
debug1: kex: server->client cipher: aes128-ctr MAC: hmac-sha2-256 compression: none
debug1: Authentications that can continue: publickey,password
"""


class Parse(unittest.TestCase):
  """Handshake facts from ssh -vv."""

  def test_old_ipssh_switch(self):
    """IPSSH 6.6.0 negotiates only the legacy set.

    Args: none.
    Returns: None.
    """
    f = p.parse(OLD)
    self.assertEqual((f["banner"], f["protocol"], f["kex"], f["hostkey"], f["cipher"], f["mac"]),
                     ("IPSSH-6.6.0", "1.99", "diffie-hellman-group1-sha1", "ssh-dss", "aes128-cbc", "hmac-md5"))
    self.assertEqual(f["auth"], "publickey,password")

  def test_new_switch_keeps_strong_algorithms(self):
    """TPSSH negotiates strong algorithms although the legacy ones are offered as fallbacks.

    Args: none.
    Returns: None.
    """
    f = p.parse(NEW)
    self.assertEqual((f["banner"], f["kex"], f["mac"]), ("TPSSH-1.0.0", "diffie-hellman-group16-sha512", "hmac-sha2-256"))

  def test_failure_is_reported(self):
    """A refused negotiation has no auth line and carries the error.

    Args: none.
    Returns: None.
    """
    f = p.parse("Unable to negotiate with 10.0.0.2 port 22: no matching host key type found. Their offer: ssh-dss\n")
    self.assertNotIn("auth", f)
    self.assertTrue(f["error"].startswith("Unable to negotiate"))


class Split(unittest.TestCase):
  """One SMC session, one transcript per address."""

  def test_split_by_marker(self):
    """Lines after each marker belong to that address.

    Args: none.
    Returns: None.
    """
    got = p.split("===IP 10.0.0.1\n" + OLD + "===IP 10.0.0.2\n" + NEW)
    self.assertEqual(sorted(got), ["10.0.0.1", "10.0.0.2"])
    self.assertIn("IPSSH", got["10.0.0.1"])
    self.assertIn("PreferredAuthentications=none", p.remote_script(["10.0.0.1"]))


if __name__ == "__main__":
  unittest.main()
