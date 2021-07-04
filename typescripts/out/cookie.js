/*
 * General utils for managing cookies in Typescript.
 */
define(["require", "exports"], function (require, exports) {
    "use strict";
    Object.defineProperty(exports, "__esModule", { value: true });
    exports.deleteCookie = exports.getCookie = exports.setCookie = void 0;
    function setCookie(name, val) {
        const date = new Date();
        const value = val;
        // Set it expire in 1000 weeks
        date.setTime(date.getTime() + (1000 * 7 * 24 * 60 * 60 * 1000));
        // Set it
        document.cookie = name + "=" + value + "; expires=" + date.toUTCString() + "; path=/";
    }
    exports.setCookie = setCookie;
    function getCookie(name) {
        const value = "; " + document.cookie;
        const parts = value.split("; " + name + "=");
        if (parts.length == 2) {
            return parts.pop().split(";").shift();
        }
        else {
            return null;
        }
    }
    exports.getCookie = getCookie;
    function deleteCookie(name) {
        const date = new Date();
        // Set it expire in -1 days
        date.setTime(date.getTime() + (-1 * 24 * 60 * 60 * 1000));
        // Set it
        document.cookie = name + "=; expires=" + date.toUTCString() + "; path=/";
    }
    exports.deleteCookie = deleteCookie;
});
//# sourceMappingURL=cookie.js.map