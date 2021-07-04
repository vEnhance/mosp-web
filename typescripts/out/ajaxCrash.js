define(["require", "exports", "sweetalert2"], function (require, exports, sweetalert2_1) {
    "use strict";
    Object.defineProperty(exports, "__esModule", { value: true });
    function err() {
        sweetalert2_1.default.fire({
            title: "Something went wrong",
            text: "Please contact Evan so we can debug this issue",
            icon: 'error',
        });
        return;
    }
    exports.default = err;
    $(() => {
        $(document).ajaxError(err);
    });
});
//# sourceMappingURL=ajaxCrash.js.map