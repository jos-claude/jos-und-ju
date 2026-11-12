"""Kompakte Kodierung der Terrain-Kanaele (muss zum Decoder in WorldBuilder/init.luau passen).

Hoehen (uint16): Vorhersage aus Nachbarn (links + oben - oben-links), Rest als Token:
  gerade Token  t = 2*zigzag(r)      -> Rest r
  ungerade Token t = 2*k + 1         -> k Reste mit Wert 0
Byte-Kanaele: Lauflaengen-Kodierung (Wert, Anzahl) als Varints.
Alles danach als Base64.
"""
from __future__ import annotations

import base64

import numpy as np


def _varint(out: bytearray, v: int):
    while v >= 128:
        out.append((v & 127) | 128)
        v >>= 7
    out.append(v)


def predict_residuals(q: np.ndarray) -> np.ndarray:
    q = q.astype(np.int64)
    pred = np.zeros_like(q)
    pred[0, 1:] = q[0, :-1]
    pred[1:, 0] = q[:-1, 0]
    pred[1:, 1:] = q[1:, :-1] + q[:-1, 1:] - q[:-1, :-1]
    return (q - pred).ravel()


def encode_heights(q: np.ndarray) -> bytes:
    r = predict_residuals(q)
    out = bytearray()
    n = r.size
    nz = np.flatnonzero(r)
    pos = 0
    for idx in nz.tolist():
        if idx > pos:
            _varint(out, 2 * (idx - pos) + 1)
        v = int(r[idx])
        z = 2 * v if v >= 0 else -2 * v - 1
        _varint(out, 2 * z)
        pos = idx + 1
    if pos < n:
        _varint(out, 2 * (n - pos) + 1)
    return bytes(out)


def decode_heights(data: bytes, n: int) -> np.ndarray:
    """Referenz-Decoder (zum Testen)."""
    res = np.zeros(n * n, np.int64)
    i = 0
    p = 0
    while i < n * n:
        t, p = _read_varint(data, p)
        if t & 1:
            i += (t - 1) // 2
        else:
            z = t // 2
            res[i] = z // 2 if z % 2 == 0 else -(z + 1) // 2
            i += 1
    res = res.reshape(n, n)
    q = np.zeros((n, n), np.int64)
    for row in range(n):
        for col in range(n):
            if row == 0:
                pred = 0 if col == 0 else q[0, col - 1]
            elif col == 0:
                pred = q[row - 1, 0]
            else:
                pred = q[row, col - 1] + q[row - 1, col] - q[row - 1, col - 1]
            q[row, col] = pred + res[row, col]
    return q


def _read_varint(data: bytes, p: int):
    v = 0
    shift = 0
    while True:
        b = data[p]
        p += 1
        v |= (b & 127) << shift
        if b < 128:
            return v, p
        shift += 7


def encode_rle(a: np.ndarray) -> bytes:
    flat = a.ravel().astype(np.int64)
    out = bytearray()
    if flat.size == 0:
        return bytes(out)
    change = np.flatnonzero(np.diff(flat)) + 1
    starts = np.concatenate([[0], change])
    ends = np.concatenate([change, [flat.size]])
    for s, e in zip(starts.tolist(), ends.tolist()):
        _varint(out, int(flat[s]))
        _varint(out, e - s)
    return bytes(out)


def to_base64_chunks(data: bytes, chunk_chars: int = 180_000) -> list[str]:
    s = base64.b64encode(data).decode("ascii")
    # Grenzen auf Vielfache von 4 legen, damit jedes Stueck fuer sich gueltig bleibt
    step = chunk_chars - chunk_chars % 4
    return [s[i:i + step] for i in range(0, len(s), step)] or [""]
