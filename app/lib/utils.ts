/**
 * Utility functions for formatting and data manipulation
 */

import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Combines multiple class names using clsx and tailwind-merge
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format a date string or Date object into a human-readable format
 * 
 * @param date - Date string in ISO format or Date object
 * @param options - Intl.DateTimeFormatOptions for customizing the format
 * @returns Formatted date string
 */
export function formatDate(
  date: string | Date | number,
  options: Intl.DateTimeFormatOptions = {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }
): string {
  const dateObj = typeof date === 'string' || typeof date === 'number' 
    ? new Date(date) 
    : date;
  
  return new Intl.DateTimeFormat('en-US', options).format(dateObj);
}

/**
 * Format a currency amount with proper currency symbol and localization
 * 
 * @param amount - Number to format as currency
 * @param currency - ISO currency code (USD, EUR, etc.)
 * @param locale - Locale for formatting (defaults to en-US)
 * @returns Formatted currency string
 */
export function formatCurrency(
  amount: number,
  currency: string = 'USD',
  locale: string = 'en-US'
): string {
  if (amount === null || amount === undefined) return '';
  
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
  }).format(amount);
}

/**
 * Truncate a string to a maximum length and add ellipsis if needed
 * 
 * @param str - String to truncate
 * @param maxLength - Maximum length before truncation
 * @returns Truncated string with ellipsis if needed
 */
export function truncateString(str: string, maxLength: number): string {
  if (!str) return '';
  return str.length > maxLength ? `${str.substring(0, maxLength)}...` : str;
}

/**
 * Format a number with thousands separators
 * 
 * @param num - Number to format
 * @param locale - Locale for formatting (defaults to en-US)
 * @returns Formatted number string
 */
export function formatNumber(
  num: number,
  locale: string = 'en-US'
): string {
  if (num === null || num === undefined) return '';
  
  return new Intl.NumberFormat(locale).format(num);
}

/**
 * Calculate the time difference between now and a given date in a human-readable format
 * 
 * @param date - Date string in ISO format or Date object
 * @returns Human readable time difference (e.g., "2 hours ago", "3 days ago")
 */
export function timeAgo(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  
  const seconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);
  
  // Less than a minute
  if (seconds < 60) {
    return 'just now';
  }
  
  // Minutes
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) {
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  }
  
  // Hours
  const hours = Math.floor(minutes / 60);
  if (hours < 24) {
    return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  }
  
  // Days
  const days = Math.floor(hours / 24);
  if (days < 30) {
    return `${days} day${days > 1 ? 's' : ''} ago`;
  }
  
  // Months
  const months = Math.floor(days / 30);
  if (months < 12) {
    return `${months} month${months > 1 ? 's' : ''} ago`;
  }
  
  // Years
  const years = Math.floor(months / 12);
  return `${years} year${years > 1 ? 's' : ''} ago`;
} 