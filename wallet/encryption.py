import os

from typing import Union, List
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from pydantic import BaseModel, Field
from fastapi import FastAPI, Query
from mangum import Mangum

from aws import retrieve_parameter

app = FastAPI()
handler = Mangum(app)
backend_pvt_k = os.environ.get("BACKEND_PVT_K") or retrieve_parameter("BACKEND_PVT_K")
backend_pub_k = os.environ.get("BACKEND_PUB_K") or retrieve_parameter("BACKEND_PUB_K")


class Encryption(BaseModel):
    message: str = Field(..., example="Encrypt me, please!")
    public_key: str = Field(..., example="2d2d2d2d2d424547494e205055424c4943204b45592d2d2d2d2d0a4d494942496a414e42676b71686b6947397730424151454641414f43415138414d49494243674b434151454130454f62426b703476334c6765416f75586d57500a4332656d58452b644d2f66584463656b4845566a70615a724f77744441326f724e3176765447634d4e49465837523339722b4b3475504d76594c56704a4361560a7337576f4b63727a586d32675a494b4e66537443562b4a416d463671715262465268586f326b6375306d57575877562b503553342f4f7871704172505457476f0a52432f57463062374d74563264586958586870762b48585367552f6a316e3157715a4f455161697a7466477573427679426f355946546b714e595344797169480a66524f704d32786d775a704748556e7156464c4563484b57776b6431646d6f392f5757386146486172446c756e6778352f4a57582b527939584d4171637553580a4a553974523273664870456b536c6c4972497237486d6347686549356c796f307869536f74625073796147466c66753336356d636846466e723663436449636e0a4b514944415141420a2d2d2d2d2d454e44205055424c4943204b45592d2d2d2d2d0a")


class Decryption(BaseModel):
    message: str = Field(..., example="84aa21bc087739bea9075ca3a391fbabfd40f149ab42f00366629737070a25253b2a8016cbf7c4aa0a2230ded2714fb7116756307a32a83527b3e82a1effba781d4f3a6950a46a47e90884e87ca9d6085bf139177c20934decfa8b927f0d85afa820474024fe5ed66c777d9e139c1dbbf5ae8db0d913fd6297dc93da1aefb0cf67efe541ea0f8d555f5cf1a03fc39c3e637390e692755b62d9f820c68f1264447784e9332ebb7fdc68d02bd7cd79f79f0681d64d403875f1a729ba4f30020debd68d5e781d443397387c10c7b964a7e65123e3a7d0df6c15c394a589d99d740369cebea247b58ee5c7f195c101d7a20cba153841e2f967bbafcd8d6613c6eac7")
    private_key: Union[str, List[str]] = Field(..., example=[
    "3b962d4e0e3789f49d9f7668e606858c9ea8db98eca208b4078b7481f352ae8b075b25ded2beecef2d98c05592a675b922038a4cb9f1fa4863ac1381fe742d456a0fb954c19201d05f01837b1d5eef878093eda72a45e9feacfa6b9d118b67063b691119545584224f32a8db9c10af5beb8ac74dea25fc5cfcad5a1e891dd4d6edaad27d8cfeb577b4931be7a7267101bc806b4488a75b823955bf4675237359ac50683100b2740d262cec70984d7a9eb5d3c19a3470495310be12d0ef833db49000aa6bedbc5282f12eb70b326604d3d19f2e8f3bc3beed850c38ec9ad89d4a61655b22b1937c7cc3d5442a68396ccccd39d7ebd9c081726fe39a67f806e2ef",
    "3357f00ae6e8bce7e6f5b6d7529aca88d3fbaa98bf8bd7a199b48dbe025158d49755aed85ef0cec9540d159d8a2045f5ec3c477f11acbda859ba02deb1b9431ad8b4e53493c40f4d32ab779810a50d8a52f48c2dff2f5d18d19cc478bc7595be1300c80ced7ef46a62eac7209cf7d18faacd6d97d9a97c60275ecd610bdc028ac9329ae3486bdb1888aabd306b1fd8de8cce16f278804a64157c371d02220a2be2ad9fbed0aeff1e5a13c3760e28f67fe1cad155c8c3ab516ca60684ddeef74b487ab0c561bb6f21ee50676438743974b0e1188e8b031e4ded062d3cf04a21db8f02f960058a1f9ea8eee3b0e33745edd06a3d825097f4f67ca6a587c501c882",
    "1c58447c5496122821f56cf55cde7b5ae21b5e28c93277bc8703c17d1e7386b18c39bb7ccee29c21d54ace46d3868581cfb3b0a5fb556be8f8cd3a15161cc1d7d149bb717a08bd8058e7c0544e1f72230254b10d8e648cccf9ee379fdab1a84023de09bcb6b07aa5b6b4e4e2bda1fedade8da85cf27aa455e475fdbf6f8e44102d33ad83c29a124ffac04a29dcfd38e6ba22eadd5a7faa8ac4d7ce3cd274a6df890096e00d2553006dc2fa5ba98483684e160c2207b0715900071cfe38f56893a419c5430322475467b6bff87c8b0b1f432f37537cf1d69af1fa0b3610bd0c2c3088be7f183f5931dac24496ceb468b9e520a1d9d53f3c60e4dc799ae0050f3e",
    "76cf0cf5bf847f25292729e0ea9bf5cb0ee7a8975f368f90ec1a2b3129f47a95741799e8ebaf03926dd8ff8c4ddf96b97aa385d480932d7c81ee43dba438da95eb0b5c51b2ec40d91646922141b122575735727cffe8cab67b62aa59da094088caf4dff90c6b3a68113f04ebcbef9a752b47b5d350401fcb55277fb06acb30f9c6222e654e8046df05a62d861b82b610978fcbbf227bf02ac6d336ec2092e27a6f2e8b43d9b2c9c8d41ad1ba83f19f84f66c025f7f234d32a91a51e482967df29605ded73e5145687f6730d4fa72d542afedb8bfdebaf475a590d2c1655d8a31093b9eece1f6b81eb09f65f6750be5e9c4af2a8b81acdd58ebb2b4dc91ed9c19",
    "2c23c50bcf2cc99ba774c468ca27a7e9847aab385116117018ea1d54a8b3be79beaa2f16e8a176bb09fe9af76ac956a53ba31ab3349848617aefb6dc3c38841d030242080264926ea26c1730bacf763806aaa66754654597e5d471b8ed7160babf28606514d0509de69495c606d20c5042e9e2caf860bc4c950caf932a902aee690848053faf16ce0d6d0c1252d3d33769559dff181dad97bebf0a5f7653ea4ee11e55cc5f24282cfc37348522ecf572799a9da26b3efff2d6cb36d2e24d9e391cba1df0b8faf4d5919ef33b869ddb14d8b1d530511bdb7f28a6e47f948b1f13bbd4c409b3a41b3bb8585f08d0aa347a6685e271093b7e5c3bdd3798656ccb8a",
    "4a57e51547fd7b77cb498314b04ea48bc1cd89105cc01d12807396dd52044afdf11ad81703f5347179d669904b1b883161793c662a5ca5aa32229b06e6aacd2e1af980313e5a676e49bc9b2ef9be678d5300a95926362bc83a3cc45696eba758392c1b82838a5f77873cae3f0aecc33b3091320d3092129c39bbd8f2ae48240a9dfd746774b4076d83f993abbf0dda9564d8d76aa5049e3ec0298c13cb43ecc544e7e0bb309f8f0949a475697d3fefec29de4ccdee2233120cbb84987fe15be481aef73bcc3c262d493a43bb6422d89e26312ac59ac02ad27c50e5db477d746559d85af6f0635b16cba97a20af8776937cbcd809ce6c14ba72309ec783ab9ac2",
    "603ff172707b3aaca8514a3ab8088c1b1606d529de0e3347a0a6cead7aaebe14f269be4cf39dd692d0b288abce8dfc3669a5389e30296a20ac2b09055e60c5f547ab9470d39338efef5f2b3a8220cae936bc24e303b2602c10d44af271269fc9c5c8de6335e904926adb7e76cef1d2c1412f233b5740ff94d1b2339036c6e8f393443a4ebfacf8b74671ae8f5dcecad743cb2315d868548ae58bc41fa411c8611799d34bcc09418fc9de5b76e5ab8dc4d0415c1385811635d39d8e13f3a5c1ad9a7baed24ba7771bb4226fbedf622ce29e4cd7e13845e5e695b419b1a47a46273dfb3afafa994033bcff0aa1bec9d2fa28b221104cae414c734fa2f213b44cbf",
    "9d1f28f9d3191cd99973e3d7b4bd1ad81d5d8cff72d62c2c17b3a07e0a2a6dff37dfd8e23af9dd88a0c6fb08ba529845d093da15dc9895c061c9a667192aa9c337a1c4a64c40ed651139ce881643f921477dabe949ab2182ba2d63fabce50cb6bd27b8cbe5b46c3eaf17245e11c06d9f2bf544288d5f462b2ee38034746597dbe99448226599e438d0bf9782944af07c76045dba616ff924b77e7f1679ca05dc3c10a975a9ed4cd9106303889263b0080119a5e5ecc0bc9433b5ab35f4e28489fa2a65253657581e6001b8169f872945d465c58fac7f01db67bee1c388dc7771acb94a14c2afe4076716903a63959e4e2a6ec7108a0867ec22bc62d4c219cbf6",
    "46cf6a2b460213f73b67eaf79dc25c2e49c50207b159430660ca7907b5f530464548cb20ac0d526767d9290562d9fffb16d9938bf0a7682257d55af370b469ae81f008f2277e69d8f204240f916ca4d6fa538b20ff2b97fbf8610efdfb06185fc981343a48d5c67458f97dab0a1840246cb17f37c0fea3e0685703cbec2eb16e96bea3830a1df1885ccfd8967750496c7a87b970a72aa4c88b9981b8a9547feebe84b747ddfeab57bb84b4940f4cf47466b1c75517dbb6d0578f6debd3ec24bd42e8c35d4836a12bd43a1f5583c2403e8875d9c5003bd7c3e073114cd1ef6a5e237bdc2e3f4c1224763695c10a392ff05f0534eddf06a0cc7542a20a88a629f9",
    "3501733c72a5ec254e7f82d8d241d8a9d985723ca0df413cef402f2862823ac61b5a184693c959be8322e3a983446617d0a76bf02132bbc8e745c49970d1fb4d421220dd98b81af0cdeb4bfc896e0e1ba4f23a2760052727394663f0189991851a9982653ae9ef608e3b393fe4e057f1bbd8fdd7b24c72fd838e23cc48ca451b624bd680eecf08070312ac57ce99e89c76f4900224624f12fcb2c4735fc93558ac3365f5be11e784b581b63dcf27d450ae11e0b24351dd7455cc4a35d6d63b2c020786107a18457452fef717576ef826a9f9c97e2bedf76d76506b864d03e28d89b1606f6a58d2d14445e1fbff84dd5ac43e2a6079fffcbb0d1887874ef22153",
    "3234a82a72df71cab29c9047d71908602a8a5d6643a533cd2f1733c5e0134d9799f05bc418fc0b5290d4eb39e1a4053e4b4396bc239d16c4f79a43ccda68baafff99b5e0b9b1c5411f0299abff95e9d883680dcc77cad2a902e373af19cd054b7bd2c84b26312af08227d66c84dade16bc0dcbedd0c1a2a6c7647bc1cdb12727dd2188e7063aaa7e6faf88b189c4416c6991d0c686138500c059361415e60dfa640bf9773c8d660d4bb40096b36a2f865a763266303290ce544c458038a6bede1eb755e764e4dc15381ff658649c89d75c6926cc3c8c284febe11f41e7e5b2c8ee7d97c2dc2fcae67c9b143d93a0108f211c3c1b64d6f12e552897c4aa0cd179",
    "9b62f560b95e9df6441dfe11c92e23e0a61bd013bdb93368992dd81e619cd9c284a3c1eff51081d20dc679af54a97633fdf845deb0376562bb6f8a80a57d61d0f7fcfd60716c2642fd0737acef0afbcc913130b54999e8683dbee00a99be344addaf2151825d847bb2a187866c74cd58daecba89d20cbef589c4abf02ff79f3492d8d56e0ebbab5421b2d5e3a522e9c3d5fc6b91b51915c686bfc8a560322583c3034043abff89c25a12f75068dcd61dafd59fbdb1e172332e1e1174f7083dd66fb7574689966e8c4cd8018d0c4ca41dc2ee19bf23147b4cc29d9fcace6eea24a84ee7ab076d4c515c0801e4c99730e3d8d4b2e5e873a8f115697f893fcfce13",
    "a123ef5e90e0a9e4202510129b75d74baac4eb5ea71bd5c16fb5b96fc93e952c5f254d49c76402dba50476d8fbf15f85172c0cd63a7e9007e50645e1ee46f8840a8f9301946e78e4cf2f8a691c690845469f4ff270257367b2a1dc4b24ac2f69fcda883247fbeee96c3d2eb78e568edd6b942da322a0ab3945413b0198ecc71fbbb9cbd05dd7f01905ad05064ac7b2b3025bdb0f5e3855df0d17b6b43fe57254cbabd37f9329fa7dbe9bc7f38be9c64163084f849c392b5bbf24e0253659dd042cb6a87ba31fba9a2a4efd773338a529402740efe98358d1fb1804ca1ad6343b71e38c13da6eeaa3e62aa2df32cf8a3f26affc5f5c4d1f73aebcb7b63dbf560f",
    "5372d479a007c7b533e29078a9607778950fbe357aa78130bed3a5acd97ec7f88e45e6c80becd56ed8471e8e0f951849f297a2aa7577defaf7b7cc782c9102722815285a22de7a2581fe9d43c809821c24844f5f7d962fb820e8b660923beea88d1ff58094154d408e2264f1f006345d4eaf16fcae36245934bdb2b784dc8411b2963eda84eb44cdb4068fff7740bcd580e586ff51de9b652a55a4ee02ce05004fb31f94c4095341935fd47e9328fcf56bb7439b2fa5b68c7be1834563e96f8edd2172ed4a603cde66b735ca07e63454ae60c147cc7bb80afc947e6e54236ef4b4102a2299635de99c0976e3a62252c0bc68ffbc44172c90e5dc873d67167c4d",
    "4b5f440f0554a13959325b5f26508f2ee6abf4a23111b545c3b48c09790767a07ccb21d0993066e8b80a9b65badf1b14a479db75facdc96859fab59c7698f2e9303930c599e768dfb9549285e2ae4f169dbaa5a4babf1c3a2a697f71feba7eec7ee05de5d32db655c43741030fa592b562590aed4a603eba6c2d9c844e1ff64842bc09ea767f8c0797ce8d7722f235dc6e1d698ac26fdc029f37bd0ec7c7293fbe1e937a939a200efdf6ed09f9d263ebb19a9abcc30503585206cacca722c180c4fa41b3aa307a5831acdbe635c32d4b8859db00da8086900b8386a8b356c3554f7d9cf7a33c6e5b1b4d2028ec8d7b04c4f3f5dbe836522f937f05a75d51ad79",
    "42bc1ab2b056a2b0bed6943d8348e205c73ad15af21bbed50903902b37347f2ca688dc52591c3e2fe26bef33cef01025575d88841aa01757a818c5ca9443128df5694da8f1429a90e272c112ebd98b846fda21f14f8cd0f8084d413d897c5352b501ade992b0f54b1509b02d67754c705a177dc64204f766d20f4f79d8c430cd6aa5575710a7e3ff7373cff707d783d4e82585728d5216c59328e3dbc0ee43411c794df1feb0dc2e2a125dba0f18f384794bdedb0eb0fdfbedabaa11c11ec96a99ef57849a36f03f5e684a2e08cdc3f981d27aabbdb9e579f7b8db973ff747dcedee8560d5ba30dcbaab9ccccd06c69d4c2fa6d1c630fa4076539b6574cd3310",
    "4b53a6ec1193d0a5b98b517e71931d1a81134caa7dbaa9e8f0258260f4942a16ef270419414063fefadeeb5db999026eb22d3dc1c5d21481624ef0c54ac1946aa6d413c557269617c12e512bcfa30c863a54a497094920fdaa293cc4e687aa8ea0c107e9b1b274d5b75ec74c03bc8e3810ab3284710985f2b384c53fc728bb5da2e0d68ddf2a1d72ce67989f0e8640bc7495a73d95328d6f0d485110f67504276d5fd3e0f9ad831b5448bd12fe98e2bd0745ca3cf03d615e73a24175add78bd5c2f62dd07abb1297c8cc486fb00f466487cbf3fc0243d9b5e0af555cfc2b0d7c0121e7da667739aada1b2e00ac1d1f59b0c5b62de3b42a18e714ddeddced7136",
    "b1b03b4f1c128627b9431bd4d09456b5eeedf52f80149a2768287103cef5bfbf39a26fe04a333d43fbc4d7ba630b74054cd2b6cb7cd4c0d8f12562539fd8a4c45e05b40c61ca2f9acc22f4fca0fce01b888eff09575b0d867c7d8d9c09dad71e32897efa10333294e79f18299d5f720a22d79a52e8d516e06948903efb005c7df288ed0361e32ae32b5faec7f0466123a1b9a0e12b23821ed40003825e4d2e775a7c4f0f6c130120380d4c9212d179c197921c01aaab31dabcdd7b44495cf2c378187cd4858a0f3ed61bac8cfc4a6ac0df1047dd940e234c02ffc9933598814772aba6ebf7a791496542abcdf849d3e1129756c382aee80a58a956997230d3cc"
  ])


@app.get("/")
def root():
    return {"RSA Key Generator": "CryptoBot_UnB_2024.1"}


@app.get("/rsa/keygen", tags=["RSA Cryptography"])
def rsa_keygen(encrypt: bool = Query(None, description="Choose if private_key will be returned encrypted", example="true")):
    """
    ```
    Generates RSA key pair and returns the public and private keys.

    If `encrypt` is True, the private key is returned in encrypted chunks.

    Query Params:
        encrypt (bool): Flag indicating whether to encrypt the private key.

    Returns:
        dict: A dictionary containing:
            - "public_key" (str): The generated public key.
            - "private_key" (str): The generated private key (if `encrypt` is False).
            - "private_encrypted_key" (list): The private key encrypted in chunks (if `encrypt` is True).
    ```
    """
    c = Cryptography()
    c.generate_keys()
    chunk = 190
    response = (
        {
            "public_key": c.keys.get("public_key"),
            "private_encrypted_key": [
                c.encrypt(
                    c.keys.get("private_key")[max(0, i - chunk) : i], backend_pub_k
                )
                for i in range(chunk, len(c.keys.get("private_key")), chunk)
            ]
            + [
                c.encrypt(
                    c.keys.get("private_key")[
                        -(len(c.keys.get("private_key")) % chunk) :
                    ],
                    backend_pub_k,
                )
            ],
        }
        if encrypt
        else {
            "public_key": c.keys.get("public_key"),
            "private_key": c.keys.get("private_key"),
        }
    )
    return response


@app.post("/rsa/encrypt", tags=["RSA Cryptography"])
def encrypt_msg(encrypt: Encryption):
    """
    ```
    Encrypts a given message using the provided public key.

    Body Args:
        message (str): Message to encrypt.
        public_key (str): Public key.

    Returns:
        dict: A dictionary containing:
            - "message" (str): The original message.
            - "encrypted_message" (str): The encrypted message.
    ```
    """
    c = Cryptography()
    try:
        return {
        "message": encrypt.message,
        "encrypted_message": c.encrypt(encrypt.message, encrypt.public_key),
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Check if message has 180 characters or less."
        }

@app.post("/rsa/decrypt", tags=["RSA Cryptography"])
def decrypt_msg(decrypt: Decryption):
    """
    ```
    Decrypts a given encrypted message using the provided private key.

    Body Args:
        message (str): Message to decrypt.
        private_key (str | list(str)): Private key or list of encrypted chunks.

    Returns:
        dict: A dictionary containing:
            - "encrypted_message" (str): The encrypted message.
            - "decrypted_message" (str): The decrypted message.
    ```
    """
    c = Cryptography()
    pvk = c.retrieve_pvk(decrypt.private_key)
    return {
        "encrypted_message": decrypt.message,
        "decrypted_message": c.decrypt(decrypt.message, pvk),
    }


class Cryptography:
    def __init__(self):
        self.__private_key = None
        self.__public_key = None

    def generate_keys(self):
        self.__private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        self.__public_key = self.__private_key.public_key()

    def load_keys(self, public_key: hex, private_key: hex):
        self.__private_key = serialization.load_pem_private_key(
            bytes.fromhex(private_key), password=None, backend=default_backend()
        )
        self.__public_key = serialization.load_pem_public_key(
            bytes.fromhex(public_key), backend=default_backend()
        )

    @property
    def keys(self):
        return {
            "private_key": (
                self.__private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                ).hex()
            ),
            "public_key": (
                self.__public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                ).hex()
            ),
        }

    def sign(self, message, private_key=None):
        if private_key:
            key_to_verify = serialization.load_pem_private_key(
                bytes.fromhex(private_key), password=None, backend=default_backend()
            )
        else:
            key_to_verify = self.__private_key
        signature = key_to_verify.sign(
            message.encode(), padding.PKCS1v15(), hashes.SHA256()
        )
        return signature.hex()

    def verify_signature(self, message, signature, public_key=None):
        if public_key:
            key_to_verify = serialization.load_pem_public_key(
                bytes.fromhex(public_key), backend=default_backend()
            )
        else:
            key_to_verify = self.__public_key
        try:
            key_to_verify.verify(
                bytes.fromhex(signature),
                message.encode(),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False

    def encrypt(self, message, public_key=None):
        if public_key:
            key_to_verify = serialization.load_pem_public_key(
                bytes.fromhex(public_key), backend=default_backend()
            )
        else:
            print("No public_key")
            key_to_verify = self.__public_key
        encrypted_message = key_to_verify.encrypt(
            message.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return encrypted_message.hex()

    def decrypt(self, encrypted_message, private_key=None):
        if private_key:
            key_to_verify = serialization.load_pem_private_key(
                bytes.fromhex(private_key), password=None, backend=default_backend()
            )
        else:
            key_to_verify = self.__private_key
        decrypted_message = key_to_verify.decrypt(
            bytes.fromhex(encrypted_message),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return decrypted_message.decode()

    def retrieve_pvk(self, pvk_chunks):
        if isinstance(pvk_chunks, List):
            pvk = "".join(
                [self.decrypt(pvk_chunk, backend_pvt_k) for pvk_chunk in pvk_chunks]
            )
        else:
            pvk = pvk_chunks
        return pvk


if __name__ == "__main__": # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")
