#!/usr/bin/env node

const BigInteger = require('big-integer');

function calculatePi(digits) {
    // Spigot algorithm for pi
    const n = digits + 10;
    const piDigits = [];
    let carry = 0;
    
    // Initialize array
    const arr = new Array(n + 1);
    for (let i = 0; i <= n; i++) {
        arr[i] = 2;
    }
    
    for (let i = 0; i < n; i++) {
        let sum = 0;
        for (let j = n; j > 0; j--) {
            sum = sum * j + arr[j] * 10;
            arr[j] = sum % (2 * j - 1);
            sum = Math.floor(sum / (2 * j - 1));
        }
        
        const digit = Math.floor(carry + sum / 10);
        piDigits.push(digit);
        carry = sum % 10;
    }
    
    return '3.' + piDigits.slice(1).join('');
}

// Main execution
if (process.argv.length !== 3) {
    console.log(`Usage: ${process.argv[1]} <number_of_digits>`);
    process.exit(1);
}

const n = parseInt(process.argv[2]);
if (isNaN(n) || n <= 0) {
    console.log('Please provide a positive integer');
    process.exit(1);
}

console.log(calculatePi(n).substring(0, n + 2));