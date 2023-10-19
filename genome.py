def generate_genome() -> str:
    pass

def convert_genome(genome: str) -> list[dict[str, int]]:
    # Genome Example
    #
    # { "type": 0, "drop_q": 1, "boost_q": -1, "max_drop_t": 1, "max_boost_t": -1, "io_boost_q": -1, "max_rr_t": -1 },
    # { "type": 1, "drop_q": -1, "boost_q": -1, "max_drop_t": -1, "max_boost_t": -1, "io_boost_q": 1, "max_rr_t": -1 }
    #
    # n (0...255) - Num Queues 
    # type (0, 1, 2) - Queue type
    # drop_queue (1...n) 0 is no drop, otherwise -1 to get the actual 
    # boost_queue (1...n) 0 is no drop
    # io_boost_queue (0...n)
    # max_drop_t (1..15)
    # max_boost_t (1..15)
    # max_rr_t (1..15)

    # 0x{00..ff}{0,1,2}{0..ff}{0..ff}{0..ff}{1..f}{1..f}{1..f}
    # Max Queue Genome 0x2fffffffff