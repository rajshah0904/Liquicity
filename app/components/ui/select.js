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
var __rest = (this && this.__rest) || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SelectItem = exports.SelectContent = exports.SelectValue = exports.SelectTrigger = exports.Select = void 0;
const React = __importStar(require("react"));
const utils_1 = require("@/lib/utils");
const lucide_react_1 = require("lucide-react");
const Select = React.forwardRef((_a, ref) => {
    var { className, children } = _a, props = __rest(_a, ["className", "children"]);
    return (<div className="relative">
      <select className={(0, utils_1.cn)("w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none", className)} ref={ref} {...props}>
        {children}
      </select>
      <lucide_react_1.ChevronDown className="absolute right-3 top-3 h-4 w-4 opacity-50 pointer-events-none"/>
    </div>);
});
exports.Select = Select;
Select.displayName = "Select";
// For compatibility with the existing component structure
const SelectTrigger = (_a) => {
    var { className, children } = _a, props = __rest(_a, ["className", "children"]);
    return (<div className={(0, utils_1.cn)("flex items-center justify-between", className)} {...props}>
    {children}
  </div>);
};
exports.SelectTrigger = SelectTrigger;
SelectTrigger.displayName = "SelectTrigger";
const SelectValue = (_a) => {
    var { className, children } = _a, props = __rest(_a, ["className", "children"]);
    return (<span className={(0, utils_1.cn)("block truncate", className)} {...props}>
    {children}
  </span>);
};
exports.SelectValue = SelectValue;
SelectValue.displayName = "SelectValue";
const SelectContent = (_a) => {
    var { className, children } = _a, props = __rest(_a, ["className", "children"]);
    return (<div className={(0, utils_1.cn)("absolute mt-1 w-full z-50 bg-background border rounded-md shadow-lg", className)} {...props}>
    {children}
  </div>);
};
exports.SelectContent = SelectContent;
SelectContent.displayName = "SelectContent";
const SelectItem = (_a) => {
    var { className, children, value } = _a, props = __rest(_a, ["className", "children", "value"]);
    return (<option className={(0, utils_1.cn)("px-3 py-2 hover:bg-accent", className)} value={value} {...props}>
    {children}
  </option>);
};
exports.SelectItem = SelectItem;
SelectItem.displayName = "SelectItem";
