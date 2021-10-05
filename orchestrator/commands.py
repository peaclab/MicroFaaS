import random
import string
from binascii import hexlify
from zlib import compress

from numpy import random as nprand

# Supported workload functions and sample inputs.
# Make sure COMMANDS.keys() matches your workers' FUNCTIONS.keys()!
# Hardcode seeds for reproducibility
random.seed("MicroFaaS", version=2)
nprand.seed(63302)
matrix_sizes = list([random.randint(2, 10) for _ in range(10)])
COMMANDS = {
    "float_operations": [{"n": random.randint(1, 10000)} for _ in range(10)],
    "cascading_sha256": [
        {  # data is 64 random chars, rounds is rand int upto 1 mil
            "data": "".join(random.choices(string.ascii_letters + string.digits, k=64)),
            "rounds": random.randint(1, 10000),
        }
        for _ in range(10)
    ],
    "cascading_md5": [
        {  # data is 64 random chars, rounds is rand int upto 1 mil
            "data": "".join(random.choices(string.ascii_letters + string.digits, k=64)),
            "rounds": random.randint(1, 10000),
        }
        for _ in range(10)
    ],
    "matmul": [
        {
            "A": nprand.random((matrix_sizes[n], matrix_sizes[n])).tolist(),
            "B": nprand.random((matrix_sizes[n], matrix_sizes[n])).tolist()
        } for n in range(10)
    ],
    "html_generation": [{"n": random.randint(1, 128)} for _ in range(10)],
    "pyaes": [
        {  # data is 16*n random chars, rounds is rand int upto 10k
            "data": "".join(random.choices(string.ascii_letters + string.digits, k=random.randint(1,10)*16)),
            "rounds": random.randint(1, 10000),
        }
        for _ in range(10)
    ],
    "zlib_decompress": [ # Having a little fun here, as random strings don't compress well
        {"data": hexlify(compress(b"It was the best of times.\nIt was the worst of times.")).decode("ascii")},
        {"data": hexlify(compress(b"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")).decode("ascii")},
        {"data": hexlify(compress(b"But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure. To take a trivial example, which of us ever undertakes laborious physical exercise, except to obtain some advantage from it? But who has any right to find fault with a man who chooses to enjoy a pleasure that has no annoying consequences, or one who avoids a pain that produces no resultant pleasure?")).decode("ascii")},
        {"data": hexlify(compress(b"We hold these truths to be self-evident, that all men are created equal, that they are endowed by their Creator with certain unalienable Rights, that among these are Life, Liberty and the pursuit of Happiness.--That to secure these rights, Governments are instituted among Men, deriving their just powers from the consent of the governed, --That whenever any Form of Government becomes destructive of these ends, it is the Right of the People to alter or to abolish it, and to institute new Government, laying its foundation on such principles and organizing its powers in such form, as to them shall seem most likely to effect their Safety and Happiness. Prudence, indeed, will dictate that Governments long established should not be changed for light and transient causes; and accordingly all experience hath shewn, that mankind are more disposed to suffer, while evils are sufferable, than to right themselves by abolishing the forms to which they are accustomed.")).decode("ascii")},
        {"data": hexlify(compress(b"Do not go gentle into that good night,\nOld age should burn and rave at close of day;\nRage, rage against the dying of the light.\n\nThough wise men at their end know dark is right,\nBecause their words had forked no lightning they\nDo not go gentle into that good night.\nGood men, the last wave by, crying how bright\nTheir frail deeds might have danced in a green bay,\nRage, rage against the dying of the light.\n\nWild men who caught and sang the sun in flight,\nAnd learn, too late, they grieved it on its way,\nDo not go gentle into that good night.\n\nGrave men, near death, who see with blinding sight\nBlind eyes could blaze like meteors and be gay,\nRage, rage against the dying of the light.\n\nAnd you, my father, there on the sad height,\nCurse, bless, me now with your fierce tears, I pray.\nDo not go gentle into that good night.\nRage, rage against the dying of the light.")).decode("ascii")},
    ],
    "regex_search": [
        {  # data is 64 random chars, pattern just looks for any digit-nondigit-digit sequence
            "data": "".join(random.choices(string.ascii_letters + string.digits, k=64)),
            "pattern": r"\d\D\d",
        }
        for _ in range(10)
    ],
    "regex_match": [
        {  # data is 64 random chars, pattern just looks for any digit-nondigit-digit sequence
            "data": "".join(random.choices(string.ascii_letters + string.digits, k=64)),
            "pattern": r"\d\D\d",
        }
        for _ in range(10)
    ],
    "redis_modify": [
        {
            "id": "".join(random.choice(["Jenny", "Jack", "Joe"])),
            "spend": str(random.randint(0,999))
    	}
        for _ in range(10)
    ],
    "redis_insert": [
        {
            "id": str(random.randint(1000000,9999999)),
            "balance": str(random.randint(0,999))
    	}
    	for _ in range(10)
    ],
    "psql_inventory": [
        # this workload doesn't actually need input, but we need something here
        # so the load generator will schedule it
        {"a": 0},
        {"a": 1},
        {"a": 2},
        {"a": 4},
    ],
    "psql_purchase": [
        {  # id is a rand int upto 60
            "id": random.randint(1, 60)
        }
        for _ in range(10)
    ],
    "upload_file": [
        # we upload files that already exist in workers' initramfs (specifically in /etc)
        # in order to avoid adding or generating dummy files at runtime 
        {"file": "group"},
        {"file": "hostname"},
        {"file": "hosts"},
        {"file": "inittab"},
        {"file": "passwd"},
        {"file": "profile"},
        {"file": "resolv.conf"},
        {"file": "shadow"},
    ],
    "download_file": [
        # we assume these files already exist in the MinIO filestore 
        {"file": "file-sample_1MB.doc"},
        {"file": "file_example_ODS_5000.ods"},
        {"file": "file_example_PPT_1MB.ppt"},
    ],
    "upload_kafka": [
        {
            "groupID": 2,
            "consumerID" : "br1-f2b841dd-1c1a-42b6-9671-0538cd17f138",
            "topic" : "SampleTopic",
            "message" : "Hello World ".join(random.choices(string.digits, k=10))
        }
        for _ in range(10)
    ],
    "read_kafka": [
        {
            "groupID": 2,
            "consumerID" : "br1-f2b841dd-1c1a-42b6-9671-0538cd17f138"
        }
    ]
}

# Reset seeds to "truly" random
random.seed()
nprand.seed()
