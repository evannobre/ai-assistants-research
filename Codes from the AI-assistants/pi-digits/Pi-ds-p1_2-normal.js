// pi_generator.js
const Decimal = require('decimal.js');

function chudnovskyPi(digits) {
    // Set precision
    Decimal.set({ precision: digits + 10 });
    
    const C = new Decimal(426880).times(Decimal.sqrt(10005));
    let K = new Decimal(6);
    let M = new Decimal(1);
    let X = new Decimal(1);
    let L = new Decimal(13591409);
    let S = new Decimal(13591409);
    
    const iterations = Math.ceil(digits / 14) + 10;
    
    for (let i = 1; i <= iterations; i++) {
        const i3 = new Decimal(i).pow(3);
        M = K.pow(3).minus(K.times(16)).times(M).div(i3);
        L = L.plus(545140134);
        X = X.times(-262537412640768000);
        S = S.plus(M.times(L).div(X));
        K = K.plus(12);
    }
    
    const pi = C.div(S);
    return pi.toString().substring(0, digits + 2);
}

// Install dependencies: npm install decimal.js
const digits = process.argv[2];
if (!digits || isNaN(digits)) {
    console.log("Usage: node pi_generator.js <digits>");
    process.exit(1);
}

console.log(`Generating ${digits} digits of Pi...`);
console.log(chudnovskyPi(parseInt(digits)));