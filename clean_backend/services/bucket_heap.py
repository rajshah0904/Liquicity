from decimal import Decimal, InvalidOperation
from typing import Dict, Tuple, List

# Buckets are stored as JSON mapping: { amount_key: rate }
# amount_key is the fiat amount (stringifiable), value is the locked USDC/fiat rate (number)

DEC_AMT_PREC = Decimal("0.01")       # 2 dp for fiat amounts
DEC_RATE_PREC = Decimal("0.000001")  # 6 dp for rates


def _to_dec(x) -> Decimal:
	return Decimal(str(x))


def _q_amt(x: Decimal) -> Decimal:
	return x.quantize(DEC_AMT_PREC)


def _q_rate(x: Decimal) -> Decimal:
	return x.quantize(DEC_RATE_PREC)


def _parse_mapping(mapping: Dict) -> List[Tuple[Decimal, Decimal]]:
	"""Convert {amount_key: rate} → list of (rate, amount)."""
	pairs: List[Tuple[Decimal, Decimal]] = []
	for k, v in (mapping or {}).items():
		try:
			amt = _q_amt(_to_dec(k))
			rate = _q_rate(_to_dec(v))
			if amt > 0 and rate > 0:
				pairs.append((rate, amt))
		except (InvalidOperation, TypeError):
			continue
	return pairs


def _rebuild_mapping(pairs: List[Tuple[Decimal, Decimal]]) -> Dict[str, float]:
	"""Serialize (rate, amount) pairs back to mapping, merging same-rate entries, sorted by rate desc."""
	agg: Dict[Decimal, Decimal] = {}
	for rate, amt in pairs:
		if amt <= 0:
			continue
		r = _q_rate(rate)
		agg[r] = agg.get(r, Decimal("0")) + _q_amt(amt)
	# Sort by rate desc; keys are amount strings, but ensure uniqueness by merging amounts per rate
	# Represent as single entry per rate: total_amount_at_rate → rate
	out: Dict[str, float] = {}
	for rate, amt in sorted(agg.items(), key=lambda x: x[0], reverse=True):
		if amt > 0:
			out[str(_q_amt(amt))] = float(rate)
	return out


def deduct_lowest_rates(mapping: Dict, amount: Decimal) -> Tuple[Dict[str, float], List[Tuple[float, float]], Decimal]:
	"""
	Deduct `amount` fiat using lowest USDC/fiat rates first.
	Returns: (updated_mapping, consumed[(amount_used, rate)], usdc_locked)
	"""
	pairs = _parse_mapping(mapping)
	pairs.sort(key=lambda x: x[0])  # rate asc
	remaining = _q_amt(_to_dec(amount))
	consumed: List[Tuple[float, float]] = []
	usdc_locked = Decimal("0")
	new_pairs: List[Tuple[Decimal, Decimal]] = []
	for rate, amt in pairs:
		if remaining <= 0:
			new_pairs.append((rate, amt))
			continue
		use = amt if amt <= remaining else remaining
		left = amt - use
		if use > 0:
			consumed.append((float(_q_amt(use)), float(rate)))
			usdc_locked += (_q_amt(use) * rate)
		remaining -= use
		if left > 0:
			new_pairs.append((rate, _q_amt(left)))
	# After loop, if still remaining, insufficient balance
	if remaining > 0:
		raised = _q_amt(_to_dec(amount)) - remaining
		raise ValueError(f"Insufficient balance: need {amount}, only {raised} available")
	return _rebuild_mapping(new_pairs), consumed, _q_amt(usdc_locked)


def add_to_rate_bucket(mapping: Dict, rate: Decimal, amount: Decimal) -> Dict[str, float]:
	"""Credit `amount` at `rate`, merging with existing same-rate entry."""
	pairs = _parse_mapping(mapping)
	r = _q_rate(_to_dec(rate))
	a = _q_amt(_to_dec(amount))
	merged = False
	for idx, (pr, pa) in enumerate(pairs):
		if pr == r:
			pairs[idx] = (pr, _q_amt(pa + a))
			merged = True
			break
	if not merged:
		pairs.append((r, a))
	return _rebuild_mapping(pairs) 