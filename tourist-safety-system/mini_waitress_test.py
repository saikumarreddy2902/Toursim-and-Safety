#!/usr/bin/env python3
"""Minimal isolated Waitress test to detect environment issues.
Run:  python mini_waitress_test.py
Then: curl http://127.0.0.1:5061/healthz
If this process also exits immediately, the issue is environmental (firewall, AV, Python install).
"""
from __future__ import annotations
from flask import Flask, jsonify

app = Flask(__name__)

@app.get('/healthz')
def healthz():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    try:
        from waitress import serve  # type: ignore
        print("[mini] Starting minimal Waitress server on 127.0.0.1:5061")
        serve(app, listen='127.0.0.1:5061')
    except Exception as e:  # pragma: no cover
        import traceback, sys
        print('[mini][FATAL]', e)
        traceback.print_exc()
        sys.exit(1)
