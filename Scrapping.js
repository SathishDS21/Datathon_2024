const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const readXlsxFile = require('read-excel-file/node');
const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

// Apply the stealth plugin to Puppeteer
puppeteer.use(StealthPlugin());

// Define input and output file paths
const inputFilePath = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/Scrapping Input data/Test_data_first.xlsx";
const outputFilePath = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/Scrapping Output data/Data_output.xlsx";

// Function to scrape data from the given URL
async function scrapeDataFromUrl(url) {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    let title = '';
    let content = '';
    let timePublished = '';
    let location = '';

    try {
        // Go to the URL
        await page.goto(url, { waitUntil: 'load', timeout: 0 });

        // Extract title
        title = await page.title();

        // Extract article content
        content = await page.$$eval('p', paragraphs => paragraphs.map(p => p.innerText).join(' '));

        // Extract time of publication
        timePublished = await page.$eval('time', el => el.getAttribute('datetime') || el.innerText).catch(() => '');

        // Extract location (if available)
        location = await page.$eval('meta[name="geo.placename"]', el => el.getAttribute('content')).catch(() => '');
    } catch (error) {
        console.log(`Error scraping URL ${url}:`, error);
    } finally {
        await browser.close();
    }

    return { title, content, timePublished, location };
}

// Function to read the input Excel file and extract URLs
async function readInputUrls(inputFilePath) {
    const rows = await readXlsxFile(inputFilePath);
    const urls = rows.map(row => row[0]); // Assuming URLs are in the first column
    return urls;
}

// Function to save scraped data to Excel
function saveToExcel(data, outputFilePath) {
    const workbook = XLSX.utils.book_new();
    const worksheetData = [
        ['URL', 'Title', 'Content', 'Time Published', 'Location'], // Header row
        ...data.map(item => [item.url, item.title, item.content, item.timePublished, item.location])
    ];
    const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Scraped Data');
    XLSX.writeFile(workbook, outputFilePath);
    console.log(`Data successfully saved to ${outputFilePath}`);
}

// Main function to orchestrate the scraping process
async function scrapeAndSave(inputFilePath, outputFilePath) {
    // Step 1: Read the input URLs from the Excel file
    const urls = await readInputUrls(inputFilePath);

    // Step 2: Initialize an empty array to store the results
    const scrapedData = [];

    // Step 3: Loop through each URL and scrape data
    for (let url of urls) {
        console.log(`Scraping URL: ${url}`);
        const result = await scrapeDataFromUrl(url);
        scrapedData.push({ url, ...result });
    }

    // Step 4: Save the scraped data to the output Excel file
    saveToExcel(scrapedData, outputFilePath);
}

// Start the scraping process
scrapeAndSave(inputFilePath, outputFilePath);