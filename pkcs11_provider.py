# NOTE: This script is test under Python 3.x

__copyright__ = "Copyright (C) 2026~2027 Nuvoton Technology Corp. All rights reserved"


import json
import pkcs11

from pkcs11 import Attribute, Mechanism
from pkcs11.util.ec import encode_named_curve_parameters


class PKCS11CryptoProvider:

    def __init__(self, config, user_pin):
        self.config = config
        self.user_pin = user_pin

        self.library_path = config["library_path"]
        self.library_path = config["library_path"]
        self.token_label = config["token_label"]
        self.aes_key_label = config["aes_key_label"]
        self.ecdsa_private_key_label = config["ecdsa_private_key_label"]
        self.ecdsa_public_key_label = config["ecdsa_public_key_label"]

    # ------------------------------------------------------------
    # Open PKCS#11
    # ------------------------------------------------------------
    def open(self):

        print("[Provider] Loading PKCS#11 library...")

        self.lib = pkcs11.lib(self.library_path)

        # Find token
        self.token = None

        for token in self.lib.get_tokens():
            if token.label.strip() == self.token_label:
                self.token = token
                break

        if self.token is None:
            raise RuntimeError(
                f"PKCS#11 token not found: {self.token_label}"
            )

        print(f"[Provider] Token: {self.token.label}")

        # Open RW session and login
        self.session = self.token.open(
            rw=True,
            user_pin=self.user_pin
        )

        print("[Provider] Login: OK")

        # Check required mechanisms
        self._check_mechanisms()

        # Find existing keys
        self._find_keys()

    # ------------------------------------------------------------
    # Mechanism check
    # ------------------------------------------------------------
    def _check_mechanisms(self):

        mechanisms = self.token.slot.get_mechanisms()

        required = {
            "CKM_AES_CFB128": Mechanism.AES_CFB128,
            "CKM_ECDSA_SHA256": Mechanism.ECDSA_SHA256
        }

        for name, mechanism in required.items():

            if mechanism not in mechanisms:
                raise RuntimeError(
                    f"Required mechanism not supported: {name}"
                )

            print(f"[Provider] {name}: OK")

    # ------------------------------------------------------------
    # Find existing keys by label
    # ------------------------------------------------------------
    def _find_keys(self):

        print("[Provider] Searching AES key...")

        self.aes_key = self._find_object(
            self.aes_key_label,
            Attribute.CLASS,
            pkcs11.ObjectClass.SECRET_KEY
        )

        if self.aes_key is None:
            raise RuntimeError(
                f"AES key not found: {self.aes_key_label}"
            )

        print(
            f"[Provider] AES key found: "
            f"{self.aes_key_label}"
        )

        print("[Provider] Searching ECDSA private key...")

        self.ecdsa_private_key = self._find_object(
            self.ecdsa_private_key_label,
            Attribute.CLASS,
            pkcs11.ObjectClass.PRIVATE_KEY
        )

        if self.ecdsa_private_key is None:
            raise RuntimeError(
                f"ECDSA private key not found: "
                f"{self.ecdsa_private_key_label}"
            )

        print(
            f"[Provider] ECDSA private key found: "
            f"{self.ecdsa_private_key_label}"
        )

        print("[Provider] Searching ECDSA public key...")

        self.ecdsa_public_key = self._find_object(
            self.ecdsa_public_key_label,
            Attribute.CLASS,
            pkcs11.ObjectClass.PUBLIC_KEY
        )

        if self.ecdsa_public_key is None:
            raise RuntimeError(
                f"ECDSA public key not found: "
                f"{self.ecdsa_public_key_label}"
            )

        print(
            f"[Provider] ECDSA public key found: "
            f"{self.ecdsa_public_key_label}"
        )

    # ------------------------------------------------------------
    # Generic object lookup
    # ------------------------------------------------------------
    def _find_object(self, label, class_attr, class_value):

        objects = self.session.get_objects({
            Attribute.LABEL: label,
            class_attr: class_value
        })

        for obj in objects:
            return obj

        return None

    # ------------------------------------------------------------
    # AES-CFB128 encryption
    # ------------------------------------------------------------
    def encrypt(self, data):

        if self.aes_key is None:
            raise RuntimeError("AES key is not loaded")

        iv = bytes(16)

        print(
            f"[Provider] AES-CFB128 encrypt "
            f"{len(data)} bytes"
        )

        encrypted = self.aes_key.encrypt(
            data,
            mechanism_param=iv,
            mechanism=Mechanism.AES_CFB128
        )

        return bytes(encrypted)

    def decrypt(self, data):
        iv = bytes(16)

        decrypted = self.aes_key.decrypt(
            data,
            mechanism_param=iv,
            mechanism=Mechanism.AES_CFB128
        )

        return bytes(decrypted)

    # ------------------------------------------------------------
    # ECDSA SHA256 signing
    # ------------------------------------------------------------
    def sign(self, data):

        if self.ecdsa_private_key is None:
            raise RuntimeError(
                "ECDSA private key is not loaded"
            )

        print(
            f"[Provider] ECDSA-SHA256 sign "
            f"{len(data)} bytes"
        )

        signature = self.ecdsa_private_key.sign(
            data,
            mechanism=Mechanism.ECDSA_SHA256
        )

        signature = bytes(signature)

        if len(signature) != 64:
            raise RuntimeError(
                f"Unexpected ECDSA signature length: "
                f"{len(signature)}"
            )

        return signature

    def verify(self, data, signature):
        if len(signature) != 64:
            raise RuntimeError(
                f"Invalid ECDSA signature length: {len(signature)}"
            )

        self.ecdsa_public_key.verify(
            data,
            signature,
            mechanism=Mechanism.ECDSA_SHA256
        )

        return True

    # ------------------------------------------------------------
    # Get EC public key X || Y
    # ------------------------------------------------------------
    def get_public_key(self):

        if self.ecdsa_public_key is None:
            raise RuntimeError(
                "ECDSA public key is not loaded"
            )

        ec_point = self.ecdsa_public_key[
            Attribute.EC_POINT
        ]

        ec_point = bytes(ec_point)

        # CKA_EC_POINT is DER encoded OCTET STRING.
        #
        # Example:
        #
        # 04 41 04 XX...YY
        #
        # DER:
        #   04       OCTET STRING
        #   41       length = 65
        #
        # EC point:
        #   04       uncompressed point
        #   XX...    X (32 bytes)
        #   YY...    Y (32 bytes)

        if ec_point[0] != 0x04:
            raise RuntimeError(
                "Unexpected CKA_EC_POINT format"
            )

        length = ec_point[1]

        if length != 65:
            raise RuntimeError(
                f"Unexpected EC point length: {length}"
            )

        point = ec_point[2:]

        if len(point) != 65:
            raise RuntimeError(
                "Invalid EC point"
            )

        if point[0] != 0x04:
            raise RuntimeError(
                "EC point is not uncompressed format"
            )

        public_x = point[1:33]
        public_y = point[33:65]

        return public_x + public_y

    # ------------------------------------------------------------
    # Split public key
    # ------------------------------------------------------------
    def split_public_key(self, public_key):

        if len(public_key) != 64:
            raise ValueError(
                "Public key must be 64 bytes"
            )

        x = public_key[:32]
        y = public_key[32:64]

        return x, y

    # ------------------------------------------------------------
    # Get labels
    # ------------------------------------------------------------
    def get_aes_key_label(self):
        return self.aes_key_label

    def get_ecdsa_private_key_label(self):
        return self.ecdsa_private_key_label

    def get_ecdsa_public_key_label(self):
        return self.ecdsa_public_key_label

    # ------------------------------------------------------------
    # Close
    # ------------------------------------------------------------
    def close(self):

        self.aes_key = None
        self.ecdsa_private_key = None
        self.ecdsa_public_key = None

        if self.session is not None:
            self.session.close()

        self.session = None
        self.token = None
        self.lib = None


