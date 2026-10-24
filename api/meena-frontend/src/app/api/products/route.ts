import { NextResponse } from 'next/server';

export async function GET() {
  const prefixes = ["Dolo", "Azithral", "Augmentin", "Pan", "Insulin", "ORS", "Amoxicillin", "Paracetamol", "Metformin"];
  const suffixes = ["650", "500mg", "625", "40mg", "10mg", "100ml", "CV"];
  
  const products = [];
  for (let i = 0; i < 1000; i++) {
    const name = `${prefixes[i % prefixes.length]} ${suffixes[i % suffixes.length]} - ${i}`;
    products.push({
      name: name,
      price: Math.floor(Math.random() * 200) + 20,
      stock: Math.floor(Math.random() * 500) + 10
    });
  }

  return NextResponse.json(products);
}
