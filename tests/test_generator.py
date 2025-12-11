import unittest
from src.models import User, Group, OU, LDAPEntry
from src.generator import LDIFGenerator
from src.validator import ValidationError

class TestLDIFGenerator(unittest.TestCase):

    def test_user_generation(self):
        user = User(uid="jdoe", parent_dn="ou=people,dc=example,dc=com", cn="John Doe", sn="Doe")
        ldif = LDIFGenerator.generate(user)
        
        expected_lines = [
            "dn: uid=jdoe,ou=people,dc=example,dc=com",
            "objectClass: top",
            "objectClass: person",
            "objectClass: organizationalPerson",
            "objectClass: inetOrgPerson",
            "uid: jdoe",
            "cn: John Doe",
            "sn: Doe"
        ]
        
        for line in expected_lines:
            self.assertIn(line, ldif)

    def test_group_generation(self):
        group = Group(cn="admins", parent_dn="ou=groups,dc=example,dc=com", members=["uid=jdoe,ou=people,dc=example,dc=com"])
        ldif = LDIFGenerator.generate(group)
        
        expected_lines = [
            "dn: cn=admins,ou=groups,dc=example,dc=com",
            "objectClass: top",
            "objectClass: groupOfNames",
            "cn: admins",
            "member: uid=jdoe,ou=people,dc=example,dc=com"
        ]
        
        for line in expected_lines:
            self.assertIn(line, ldif)

    def test_ou_generation(self):
        ou = OU(name="people", parent_dn="dc=example,dc=com")
        ldif = LDIFGenerator.generate(ou)
        
        self.assertIn("dn: ou=people,dc=example,dc=com", ldif)
        self.assertIn("objectClass: organizationalUnit", ldif)
        self.assertIn("ou: people", ldif)

    def test_batch_generation(self):
        user1 = User(uid="u1", parent_dn="dc=x", cn="U1", sn="S1")
        user2 = User(uid="u2", parent_dn="dc=x", cn="U2", sn="S2")
        
        ldif = LDIFGenerator.generate([user1, user2])
        
        self.assertIn("dn: uid=u1,dc=x", ldif)
        self.assertIn("dn: uid=u2,dc=x", ldif)
        self.assertEqual(ldif.count("dn:"), 2)
        # Check separation by empty line
        self.assertIn("\n\n", ldif)

    def test_mixed_batch(self):
        ou = OU(name="dev", parent_dn="dc=x")
        user = User(uid="u1", parent_dn="ou=dev,dc=x", cn="U1", sn="S1")
        group = Group(cn="devs", parent_dn="ou=dev,dc=x", members=["uid=u1,ou=dev,dc=x"])
        
        ldif = LDIFGenerator.generate([ou, user, group])
        
        self.assertIn("dn: ou=dev,dc=x", ldif)
        self.assertIn("dn: uid=u1,ou=dev,dc=x", ldif)
        self.assertIn("dn: cn=devs,ou=dev,dc=x", ldif)
        self.assertEqual(ldif.count("dn:"), 3)

    def test_base64_encoding(self):
        # Attribute starting with space
        user = User(uid="test", parent_dn="dc=x", cn=" Test", sn="Test")
        ldif = LDIFGenerator.generate(user)
        
        # " Test" in base64 is "IFRlc3Q="
        self.assertIn("cn:: IFRlc3Q=", ldif)
        
        # Attribute with non-ascii
        user_utf8 = User(uid="utf8", parent_dn="dc=x", cn="Jöhn", sn="Döe")
        ldif = LDIFGenerator.generate(user_utf8)
        
        # Jöhn in base64: Siwobm
        # Döe in base64: RMO2ZQ==
        # Note: base64 encoding depends on utf-8 bytes.
        import base64
        cn_b64 = base64.b64encode("Jöhn".encode("utf-8")).decode("ascii")
        self.assertIn(f"cn:: {cn_b64}", ldif)

    def test_validation_error(self):
        # Invalid DN char (comma is allowed as separator, but let's say we have a messed up DN structure)
        # Our validator is simple: checks for key=value pairs.
        # "invalid" is not key=value
        
        # We manually construct LDAPEntry to bypass User constructor checks if any (User constructor forces structure)
        entry = LDAPEntry(rdn="invalid", parent_dn="", object_classes=[])
        
        with self.assertRaises(ValidationError):
            LDIFGenerator.generate(entry)

    def test_multi_valued_attributes(self):
        user = User(uid="jdoe", parent_dn="dc=x", cn="John Doe", sn="Doe", 
                   additional_attributes={"mail": ["john@example.com", "jdoe@example.com"]})
        
        ldif = LDIFGenerator.generate(user)
        self.assertIn("mail: john@example.com", ldif)
        self.assertIn("mail: jdoe@example.com", ldif)

    def test_dn_escaping(self):
        # User with special chars in UID
        # Special chars: , + " \ < > ;
        uid = "Smith, John"
        user = User(uid=uid, parent_dn="dc=x", cn="John Smith", sn="Smith")
        
        # RDN should be uid=Smith\, John
        self.assertEqual(user.rdn, "uid=Smith\\, John")
        
        ldif = LDIFGenerator.generate(user)
        # DN should be escaped
        self.assertIn("dn: uid=Smith\\, John,dc=x", ldif)
        
        # Another case
        group = Group(cn="#admins", parent_dn="dc=x")
        # RDN should be cn=\#admins
        self.assertEqual(group.rdn, "cn=\\#admins")
        
        ldif_group = LDIFGenerator.generate(group)
        self.assertIn("dn: cn=\\#admins,dc=x", ldif_group)

if __name__ == '__main__':
    unittest.main()
