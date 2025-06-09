"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const dotenv_1 = __importDefault(require("dotenv"));
// Load environment variables
dotenv_1.default.config();
console.log('Liquicity Payment System');
console.log('Environment:', process.env.NODE_ENV || 'development');
// Main application function
function main() {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            console.log('Application starting...');
            // Add your application logic here
            console.log('Application initialized successfully.');
        }
        catch (error) {
            console.error('Error starting application:', error);
            process.exit(1);
        }
    });
}
// Run the application
main().catch(console.error);
