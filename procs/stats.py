import asyncio
async def main(pk, row, arg):
    #print("[[[[[[[[[[[STATS]]]]]]]]]]]]", pk, row, arg)
    damean = row['ts'].mean()
    dastd = row['ts'].std()
    return [damean, dastd]
