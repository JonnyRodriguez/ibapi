from time import sleep
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.order_state import OrderState
from ibapi.common import OrderId
from decimal import Decimal
from threading import Thread


class IBapi(EWrapper, EClient):
	_thread = None
	_reqid = 0

	def __init__(self):
		EClient.__init__(self, self)
		self.result = {}

	def init(self, host, port, id):
		if self._thread is None:
			self.connect(host, port, id)
			self._thread = Thread(target=self.run, daemon=True)
			self._thread.start()

	def getResult(self, reqId, maxSecs=3):
		for x in range(maxSecs*10):
			if result := self.result.get(reqId):
				del self.result[reqId]
				return result
			sleep(0.1)
		return None

	def getPositions(self):
		self._positions = []
		self.positions = True
		self.reqPositions()
		while self.positions:
			sleep(0.1)
		return self._positions

	def position(self, account: str, contract: Contract, position: Decimal, avgCost: float):
		self._positions.append(
			{"account": account, "contract": contract, "position": position, "avgCost": avgCost})

	def positionEnd(self):
		self.positions = False

	def getOrders(self):
		self._orders = {}
		self.orders = True
		self.reqAllOpenOrders()
		while self.orders:
			sleep(1)
		return self._orders

	def openOrder(self, orderId: OrderId, contract: Contract, order: Order, orderState: OrderState):
		self._orders[orderId] = {
			"orderId": orderId, "contract": contract, "order": order, "orderState": orderState}

	def openOrderEnd(self):
		self.orders = False

	def tickPrice(self, reqId, tickType, price, attrib):
		self.result[reqId] = {"tickType": tickType,
							  "price": price, "attrib": attrib}

	def contract(self, symbol, secType, exchange='SMART', currency='USD'):
		contract = Contract()
		contract.symbol = symbol
		contract.secType = secType
		contract.exchange = exchange
		contract.currency = currency
		return contract

	def getSymbolPrice(self, symbol, secType):
		self._reqid += 1
		reqId = self._reqid
		contract = self.contract(symbol, secType)
		self.reqMktData(reqId, contract, '', False, False, [])
		return self.getResult(reqId)
