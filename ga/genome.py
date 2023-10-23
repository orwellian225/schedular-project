import random
import math as m

def random_genome() -> int:
    genome_bit_length = 772
    genome = 2**genome_bit_length - 1

    for _ in range(random.randint(1, genome_bit_length * 20)):
        genome ^= 1 << random.randint(0, genome_bit_length - 1)

    return genome
    
# This requires domain knowledge so I'm assuming a couple things
def construct_scheduler_structure(genome: int) -> list[dict[str, int]]:
    num_queue_types = 3
    num_queues = ( genome >> 768 ) + 1

    structure = []

    queue_genome_length = 48
    for i in range(num_queues):
        queue_genome = ( genome >> (768 - (i + 1) * queue_genome_length) ) & (2**queue_genome_length - 1)

        queue_type = ( queue_genome >> (queue_genome_length - 2 ) ) % num_queue_types
        queue_drop = (( queue_genome >> queue_genome_length - 6 ) & 0xf ) % num_queues 
        queue_boost = (( queue_genome >> queue_genome_length - 12 ) & 0xf ) % num_queues
        queue_io_boost = (( queue_genome >> queue_genome_length - 16 ) & 0xf ) % num_queues
        queue_drop_t = ( queue_genome >> queue_genome_length - 24 ) & 0xff
        queue_boost_t = ( queue_genome >> queue_genome_length - 32 ) & 0xff
        queue_rr_t = ( queue_genome >> queue_genome_length - 40 ) & 0xff

        structure.append({
            "type": queue_type, 
            "drop_q": queue_drop if queue_drop != i else -1,
            "boost_q": queue_boost if queue_boost != i else -1,
            "io_boost_q": queue_io_boost if queue_io_boost != i else -1,
            "max_drop_t": queue_drop_t,
            "max_boost_t": queue_boost_t,
            "max_rr_t": queue_rr_t
        })

    return structure

# a - the first parent 
# b - the second parent 
# segment_length - how long of a bit segment to choose from each parent
# bias - how likely to choose a's segment over b's segment
def genome_crossover(a: int, b: int, segment_length: int, bias: float = 0.5) -> int:
    new_genome = 0

    a_len = len(bin(a)) - 2
    b_len = len(bin(b)) - 2

    num_segments = m.ceil(a_len / segment_length)

    for i in range(num_segments):
        mask = ((1 << (segment_length)) - 1) << (i * segment_length)
        clear_mask = ~(((1 << segment_length) - 1) << (i * segment_length))

        a_segment = (a & mask) >> (i * segment_length)
        b_segment = (b & mask) >> (i * segment_length)

        new_genome &= clear_mask

        result = random.uniform(0, 1)
        if (result < bias):
            new_genome |= a_segment << (i * segment_length)
        else:
            new_genome |= b_segment << (i * segment_length)

    return new_genome

def genome_mutation(genome: int, genome_length: int, num_mutations: int) -> int:
    for _ in range(num_mutations):
        genome ^= 1 << random.randint(0, genome_length - 1)

    return genome 
