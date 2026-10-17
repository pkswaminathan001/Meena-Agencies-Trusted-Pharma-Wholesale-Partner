#!/bin/bash
# Meena Agencies — Full test suite

cd "$(dirname "$0")/.."

echo "═══════════════════════════════════════════════════════"
echo "  MEENA AGENCIES — FULL TEST SUITE"
echo "  Started: $(date)"
echo "═══════════════════════════════════════════════════════"
echo ""

echo "─── 1. COMPILE CHECK ───"
python3 -m py_compile apps_isolated/meena.py && echo "  PASS meena.py" || echo "  FAIL meena.py"
python3 -m py_compile apps_isolated/block1_helpers.py && echo "  PASS block1_helpers.py" || echo "  FAIL block1_helpers.py"
python3 -m py_compile apps_isolated/block15_otp.py && echo "  PASS block15_otp.py" || echo "  FAIL block15_otp.py"
python3 -m py_compile apps_isolated/security_layer.py && echo "  PASS security_layer.py" || echo "  FAIL security_layer.py"
echo ""

echo "─── 2. FILE PERMISSIONS ───"
for f in retailers.json orders.json users.json payments.json sessions.json rate_limit.json .groq_key .meena_salt; do
    if [ -f "$f" ]; then
        perm=$(stat -c "%a" "$f")
        if [ "$perm" = "600" ]; then echo "  PASS $f ($perm)"; else echo "  WARN $f ($perm — should be 600)"; fi
    fi
done
echo ""

echo "─── 3. APP STATUS ───"
curl -s http://localhost:8501/_stcore/health | grep -q "ok" && echo "  PASS App responding" || echo "  FAIL App not running"
echo ""

echo "─── 4. FUNCTION CHECK ───"
python3 -c "
import ast
src = open('apps_isolated/meena.py').read()
tree = ast.parse(src)
funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
required = ['main','render_sidebar','owner_payments','place_order_with_approval',
            'evaluate_credit_rule','owner_ai_analyzer','owner_commandments',
            'owner_security','owner_expiry','owner_salespeople','page_owner_map']
for f in required:
    print(('  PASS ' if f in funcs else '  FAIL ') + f)
"
echo ""

echo "─── 5. AUTOMATED TESTS ───"
if [ -f tests/test_meena.py ]; then
    python3 tests/test_meena.py 2>&1 | tail -12
fi
echo ""

echo "─── 6. TELEGRAM ───"
python3 -c "
import sys; sys.path.insert(0,'apps_isolated')
try:
    from block15_otp import _tg_send
    ok, msg = _tg_send('Test from run_all_tests.sh')
    print('  PASS Telegram OK' if ok else '  FAIL Telegram: ' + str(msg))
except Exception as e:
    print('  FAIL Telegram error: ' + str(e))
" 2>/dev/null
echo ""

echo "─── 7. GROQ API ───"
if [ -f .groq_key ]; then
    KEY=$(cat .groq_key | tr -d '[:space:]')
    RESPONSE=$(curl -s -X POST "https://api.groq.com/openai/v1/chat/completions" \
        -H "Authorization: Bearer $KEY" \
        -H "Content-Type: application/json" \
        -d '{"model":"openai/gpt-oss-120b","messages":[{"role":"user","content":"hi"}],"max_tokens":5}' \
        2>/dev/null | head -c 200)
    if echo "$RESPONSE" | grep -q "choices"; then
        echo "  PASS Groq API working"
    else
        echo "  FAIL Groq: $RESPONSE"
    fi
fi
echo ""

echo "═══════════════════════════════════════════════════════"
echo "  FINISHED: $(date)"
echo "═══════════════════════════════════════════════════════"
