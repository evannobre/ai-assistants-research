#!/usr/bin/env python3
"""
Reverse Complement DNA Sequence Processor

Author: Computer Scientist specializing in back-end development
Date: 2024
Description: Efficiently processes DNA sequences to generate reverse complements
using native Python libraries with minimal memory footprint.
"""

import sys
import os
import argparse
import gzip
import mmap
import time
from typing import Generator, TextIO, BinaryIO
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FileType(Enum):
    """Supported file types"""
    PLAIN = 'plain'
    GZIP = 'gzip'
    FASTQ = 'fastq'
    FASTA = 'fasta'


@dataclass
class ProcessingStats:
    """Statistics for processing"""
    sequences_processed: int = 0
    total_bases: int = 0
    processing_time: float = 0.0
    memory_peak_mb: float = 0.0


class ReverseComplement:
    """Main reverse complement processor"""
    
    # DNA complement mapping (extended for ambiguous bases)
    COMPLEMENT_TABLE = str.maketrans({
        'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G',
        'a': 't', 't': 'a', 'g': 'c', 'c': 'g',
        'N': 'N', 'n': 'n',
        'R': 'Y', 'Y': 'R', 'S': 'S', 'W': 'W',
        'K': 'M', 'M': 'K', 'B': 'V', 'V': 'B',
        'D': 'H', 'H': 'D', 'r': 'y', 'y': 'r',
        's': 's', 'w': 'w', 'k': 'm', 'm': 'k',
        'b': 'v', 'v': 'b', 'd': 'h', 'h': 'd'
    })
    
    # Valid DNA characters for validation
    VALID_BASES = set('ATCGNatcgnRYSSWKMBDHVrysswkmbdhvNn')
    
    @staticmethod
    def reverse_complement_sequence(sequence: str) -> str:
        """
        Generate reverse complement of a DNA sequence.
        
        Args:
            sequence: DNA sequence string
            
        Returns:
            Reverse complemented sequence
        """
        # Validate input
        invalid_chars = set(sequence) - ReverseComplement.VALID_BASES
        if invalid_chars:
            logger.warning(f"Sequence contains invalid characters: {invalid_chars}")
        
        # Efficient reverse complement using translation table
        return sequence.translate(ReverseComplement.COMPLEMENT_TABLE)[::-1]
    
    @staticmethod
    def process_chunk(chunk: str, chunk_id: int = 0) -> str:
        """
        Process a chunk of DNA sequence.
        
        Args:
            chunk: DNA sequence chunk
            chunk_id: Identifier for the chunk
            
        Returns:
            Reverse complemented chunk
        """
        return ReverseComplement.reverse_complement_sequence(chunk)


class DNAFileProcessor:
    """Handles DNA file reading and writing"""
    
    @staticmethod
    def detect_file_type(filepath: str) -> FileType:
        """Detect file type based on extension and content"""
        path = Path(filepath)
        
        # Check extension
        if path.suffix.lower() == '.gz':
            return FileType.GZIP
        elif path.suffix.lower() in ['.fastq', '.fq']:
            return FileType.FASTQ
        elif path.suffix.lower() in ['.fasta', '.fa', '.fna']:
            return FileType.FASTA
        else:
            return FileType.PLAIN
    
    @staticmethod
    def open_file(filepath: str, mode: str = 'r'):
        """Open file with appropriate handler based on type"""
        file_type = DNAFileProcessor.detect_file_type(filepath)
        
        if file_type == FileType.GZIP:
            return gzip.open(filepath, mode + 't', encoding='utf-8')
        else:
            return open(filepath, mode, encoding='utf-8')
    
    @staticmethod
    def read_sequences(filepath: str, chunk_size: int = 1024 * 1024) -> Generator[str, None, None]:
        """
        Read DNA sequences from file in chunks.
        
        Args:
            filepath: Path to DNA file
            chunk_size: Size of chunks to read (default: 1MB)
            
        Yields:
            DNA sequence chunks
        """
        try:
            with DNAFileProcessor.open_file(filepath, 'r') as f:
                buffer = ''
                
                for line in f:
                    line = line.strip()
                    
                    # Skip empty lines and headers
                    if not line or line.startswith('>') or line.startswith('@') or line.startswith('+'):
                        continue
                    
                    buffer += line
                    
                    # Yield chunks of appropriate size
                    while len(buffer) >= chunk_size:
                        yield buffer[:chunk_size]
                        buffer = buffer[chunk_size:]
                
                # Yield remaining buffer
                if buffer:
                    yield buffer
                    
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {e}")
            raise
    
    @staticmethod
    def memory_map_file(filepath: str):
        """
        Memory map a file for efficient large file processing.
        
        Args:
            filepath: Path to file
            
        Returns:
            Memory mapped file object
        """
        try:
            with open(filepath, 'rb') as f:
                return mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        except Exception as e:
            logger.error(f"Error memory mapping file {filepath}: {e}")
            raise


class PerformanceMonitor:
    """Monitor system performance during processing"""
    
    @staticmethod
    def get_memory_usage():
        """Get current memory usage in MB"""
        try:
            with open('/proc/self/status', 'r') as f:
                for line in f:
                    if line.startswith('VmRSS:'):
                        return int(line.split()[1]) / 1024  # Convert kB to MB
        except:
            return 0.0
    
    @staticmethod
    def check_system_resources():
        """Check if system has sufficient resources"""
        import shutil
        
        # Check disk space
        total, used, free = shutil.disk_usage("/")
        if free < 1024 * 1024 * 1024:  # Less than 1GB free
            logger.warning(f"Low disk space: {free / (1024**3):.2f} GB free")
        
        # Check available RAM (using psutil if available, otherwise estimate)
        try:
            import psutil
            available_ram = psutil.virtual_memory().available / (1024**3)  # GB
            if available_ram < 1:  # Less than 1GB available
                logger.warning(f"Low available RAM: {available_ram:.2f} GB")
        except ImportError:
            logger.info("psutil not installed, skipping detailed RAM check")


def validate_dna_sequence(sequence: str) -> bool:
    """Validate if string contains valid DNA characters"""
    return all(c in ReverseComplement.VALID_BASES for c in sequence.upper())


def process_file(
    input_file: str,
    output_file: str = None,
    chunk_size: int = 1024 * 1024,  # 1MB chunks
    max_workers: int = None,
    validate: bool = False,
    stats: bool = False
) -> ProcessingStats:
    """
    Main processing function for reverse complement generation.
    
    Args:
        input_file: Input DNA file path
        output_file: Output file path (optional)
        chunk_size: Size of processing chunks in bytes
        max_workers: Maximum number of worker threads
        validate: Validate DNA sequences
        stats: Enable statistics collection
        
    Returns:
        ProcessingStats object with processing statistics
    """
    start_time = time.time()
    processing_stats = ProcessingStats()
    
    # Determine optimal number of workers
    if max_workers is None:
        import multiprocessing
        max_workers = min(multiprocessing.cpu_count(), 4)  # Cap at 4 for I/O bound tasks
    
    # Check system resources
    PerformanceMonitor.check_system_resources()
    
    # Determine output file
    if output_file is None:
        input_path = Path(input_file)
        output_file = str(input_path.parent / f"{input_path.stem}_reverse_complement{input_path.suffix}")
    
    logger.info(f"Processing {input_file}")
    logger.info(f"Output: {output_file}")
    logger.info(f"Chunk size: {chunk_size:,} bytes")
    logger.info(f"Workers: {max_workers}")
    
    try:
        # Process file
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            with DNAFileProcessor.open_file(output_file, 'w') as out_f:
                futures = []
                chunk_id = 0
                
                for chunk in DNAFileProcessor.read_sequences(input_file, chunk_size):
                    # Update statistics
                    processing_stats.sequences_processed += 1
                    processing_stats.total_bases += len(chunk)
                    
                    # Validate if requested
                    if validate and not validate_dna_sequence(chunk):
                        logger.warning(f"Chunk {chunk_id} contains invalid DNA characters")
                    
                    # Submit chunk for processing
                    future = executor.submit(ReverseComplement.process_chunk, chunk, chunk_id)
                    futures.append(future)
                    chunk_id += 1
                    
                    # Write results as they complete
                    for future in as_completed(futures):
                        result = future.result()
                        out_f.write(result)
                        futures.remove(future)
                        break
                
                # Process any remaining futures
                for future in as_completed(futures):
                    result = future.result()
                    out_f.write(result)
        
        # Calculate processing time
        processing_stats.processing_time = time.time() - start_time
        
        # Get memory usage
        processing_stats.memory_peak_mb = PerformanceMonitor.get_memory_usage()
        
        if stats:
            logger.info(f"Processing completed in {processing_stats.processing_time:.2f} seconds")
            logger.info(f"Sequences processed: {processing_stats.sequences_processed}")
            logger.info(f"Total bases: {processing_stats.total_bases:,}")
            logger.info(f"Peak memory usage: {processing_stats.memory_peak_mb:.2f} MB")
            if processing_stats.processing_time > 0:
                logger.info(f"Processing speed: {processing_stats.total_bases / processing_stats.processing_time:,.0f} bases/second")
        
        return processing_stats
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        # Clean up output file on error
        if os.path.exists(output_file):
            os.remove(output_file)
        raise


def main():
    """Main entry point with command-line interface"""
    parser = argparse.ArgumentParser(
        description='Generate reverse complement of DNA sequences',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s dna_sequence.fasta
  %(prog)s large_sequence.fastq.gz -o output.fastq
  %(prog)s input.fa --chunk-size 2097152 --validate --stats
  %(prog)s input.fa --workers 2 --no-stats
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Input DNA file (FASTA, FASTQ, plain text, optionally gzipped)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file (default: <input>_reverse_complement.<ext>)'
    )
    
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=1024 * 1024,
        help='Chunk size in bytes (default: 1048576 = 1MB)'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        help='Number of worker threads (default: min(cpu_count, 4))'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate DNA sequences'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        default=True,
        help='Show processing statistics (default: True)'
    )
    
    parser.add_argument(
        '--no-stats',
        action='store_false',
        dest='stats',
        help='Do not show processing statistics'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Validate input file
    if not os.path.exists(args.input_file):
        logger.error(f"Input file not found: {args.input_file}")
        sys.exit(1)
    
    # Check file size
    file_size = os.path.getsize(args.input_file)
    logger.info(f"Input file size: {file_size:,} bytes ({file_size / (1024**2):.2f} MB)")
    
    # Adjust chunk size for very small files
    if file_size < args.chunk_size:
        args.chunk_size = max(4096, file_size // 4)
        logger.info(f"Adjusted chunk size to {args.chunk_size:,} bytes")
    
    try:
        # Process the file
        stats = process_file(
            input_file=args.input_file,
            output_file=args.output,
            chunk_size=args.chunk_size,
            max_workers=args.workers,
            validate=args.validate,
            stats=args.stats
        )
        
        logger.info("Reverse complement generation completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()