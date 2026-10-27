print("== 1. een gewone class gooien ==")
class GeenFout:
    pass
try:
    raise GeenFout()
except TypeError as e:
    print("TypeError ->", e)

print("== 2. erven van een andere fout dan Exception ==")
class LLMError(ConnectionError):
    pass
try:
    raise LLMError("geen verbinding met Ollama")
except ConnectionError as e:
    print("opgevangen door 'except ConnectionError' ->", type(e).__name__, "|", e)

print("== 3. een familie van eigen fouten ==")
class LLMError(Exception):
    pass
class LLMTimeoutError(LLMError):
    pass
class LLMConnectError(LLMError):
    pass

for fout in [LLMTimeoutError("te traag"), LLMConnectError("geen verbinding")]:
    try:
        raise fout
    except LLMError as e:
        print("'except LLMError' vangt", type(e).__name__)

try:
    raise LLMConnectError("geen verbinding")
except LLMTimeoutError:
    print("'except LLMTimeoutError' vangt hem")
except LLMError as e:
    print("'except LLMTimeoutError' vangt hem NIET; 'except LLMError' wel ->", type(e).__name__)

print("== 4. twee ouders ==")
class LLMTimeoutError2(LLMError, TimeoutError):
    pass
try:
    raise LLMTimeoutError2("te traag")
except TimeoutError as e:
    print("opgevangen door 'except TimeoutError' ->", type(e).__name__)
print("is ook een LLMError:", isinstance(LLMTimeoutError2("x"), LLMError))
