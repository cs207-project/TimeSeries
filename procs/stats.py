import asyncio
async def main(pk, row, arg):
    print("[[[[[[[[[[[STATS]]]]]]]]]]]]", pk, row, arg)
    damean = row['ts'].mean()
    await asyncio.sleep(1)
    dastd = row['ts'].std()
    return [damean, dastd]
