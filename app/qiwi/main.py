from os import getenv
from time import time

import aiohttp
import asyncio


class QApi:
    """
    Манипуляции напрямую с Qiwi API
    """

    def __init__(self, token: str, account: str):
        self.TOKEN = token
        self.ACCOUNT = account
        self.headers = {"authorization": "Bearer " + token}
        self._session: aiohttp.ClientSession = None

    @property
    def num(self):
        return self.ACCOUNT

    @property  # <- уже исполниная функция без абьедка
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = self.get_new_session()
        return self._session

    @property
    def _transaction_id(self):
        """
        Generates transaction id for pay() function.
        :return: UNIX time * 1000
        """
        return str(int(time() * 1000))

    def get_new_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(headers=self.headers)

    @property
    async def balance(self):
        url = f"https://edge.qiwi.com/funding-sources/v2/persons/{self.ACCOUNT}/accounts"

        response = await self.session.get(url)
        response_json = await response.json()

        return response_json['accounts'][0]['balance']

    async def last_transactions(self, rows: int):
        url = f"https://edge.qiwi.com/payment-history/v2/persons/{self.ACCOUNT}/payments"

        response = await self.session.get(url, params={"rows": rows})
        return await response.json()

    async def last_recharges(self, sum: int):
        url = f"https://edge.qiwi.com/payment-history/v2/persons/{self.ACCOUNT}/payments"

        response = await self.session.get(url, params={"rows": 50})
        response_json = await response.json()

        payments = []

        for payment in response_json['data']:
            if len(payments) >= sum:
                break

            if payment['type'] == "IN":
                payments.append(payment)

        return payments

    async def pay(self, account: str, amount, currency="643", comment=None):
        url = "https://edge.qiwi.com/sinap/api/v2/terms/99/payments"

        params = {
            "id": self._transaction_id,
            "sum": {
                "amount": amount,
                "currency": currency
            },
            "paymentMethod": {
                "type": "Account",
                "accountId": "643"
            },
            "fields": {
                "account": account
            }
        }

        response = await self.session.post(url, json=params)
        return await response.json()

    async def close(self):
        session = self.session  # bugfix
        if session is not None:
            await session.close()

# async def main():
# 	resp = await last_transactions(3)
# 	print(resp['data'])
# 	await self.close()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
