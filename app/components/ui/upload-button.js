"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.UploadButton = UploadButton;
const React = __importStar(require("react"));
const utils_1 = require("@/lib/utils");
const button_1 = require("./button");
const lucide_react_1 = require("lucide-react");
function UploadButton({ accept = "image/*", onChange, className }) {
    const inputRef = React.useRef(null);
    const [fileName, setFileName] = React.useState(null);
    const handleClick = () => {
        var _a;
        (_a = inputRef.current) === null || _a === void 0 ? void 0 : _a.click();
    };
    const handleChange = (e) => {
        var _a;
        const file = ((_a = e.target.files) === null || _a === void 0 ? void 0 : _a[0]) || null;
        if (file) {
            setFileName(file.name);
            onChange(file);
        }
    };
    return (<div className={(0, utils_1.cn)("flex flex-col items-start gap-2", className)}>
      <button_1.Button type="button" variant="outline" onClick={handleClick} className="w-full flex items-center justify-center gap-2">
        <lucide_react_1.Upload className="h-4 w-4"/>
        <span>{fileName ? "Change file" : "Upload file"}</span>
      </button_1.Button>
      
      <input type="file" ref={inputRef} accept={accept} onChange={handleChange} className="hidden"/>
      
      {fileName && (<p className="text-sm text-muted-foreground truncate w-full">
          {fileName}
        </p>)}
    </div>);
}
