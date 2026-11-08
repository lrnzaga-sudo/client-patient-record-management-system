window.addEventListener('pageshow', () => {
    const loginForm = document.getElementById('login-form');
    if (!loginForm) return;

    loginForm.reset();
    loginForm.querySelectorAll('input[name="username"], input[name="password"]').forEach((field) => {
        field.value = '';
        field.readOnly = true;
    });
    if (loginForm.contains(document.activeElement)) document.activeElement.blur();
});

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.querySelectorAll('input[name="username"], input[name="password"]').forEach((field) => {
            field.addEventListener('focus', () => {
                if (field.readOnly) field.value = '';
                field.readOnly = false;
            });
        });
    }

    const focusStorageKey = 'clinic-auto-search-focus';
    try {
        const savedFocus = JSON.parse(sessionStorage.getItem(focusStorageKey) || 'null');
        sessionStorage.removeItem(focusStorageKey);
        if (savedFocus && savedFocus.path === window.location.pathname) {
            const field = document.getElementById(savedFocus.id);
            if (field) {
                field.focus({ preventScroll: true });
                field.setSelectionRange(savedFocus.start, savedFocus.end);
            }
        }
    } catch (_) {
        // Focus restoration is an enhancement; search still works if storage is unavailable.
    }

    document.querySelectorAll('form[data-auto-submit]').forEach((form) => {
        let submitTimer;

        const submitForm = (focusField = null) => {
            if (focusField && focusField.hasAttribute('data-restore-focus')) {
                try {
                    sessionStorage.setItem(focusStorageKey, JSON.stringify({
                        id: focusField.id,
                        start: focusField.selectionStart,
                        end: focusField.selectionEnd,
                        path: new URL(form.action, window.location.href).pathname
                    }));
                } catch (_) {
                    // Focus restoration is an enhancement; search still works if storage is unavailable.
                }
            }
            if (typeof form.requestSubmit === 'function') {
                form.requestSubmit();
            } else {
                form.submit();
            }
        };

        form.querySelectorAll('[data-auto-submit-input]').forEach((field) => {
            field.addEventListener('input', () => {
                window.clearTimeout(submitTimer);
                submitTimer = window.setTimeout(() => submitForm(field), 250);
            });
        });

        form.querySelectorAll('[data-auto-submit-change]').forEach((field) => {
            field.addEventListener('change', () => {
                window.clearTimeout(submitTimer);
                submitForm();
            });
        });
    });

    document.querySelectorAll('[data-patient-search]').forEach((search) => {
        const select = document.getElementById(search.dataset.patientSearch);
        if (!select) return;

        const options = Array.from(select.options).filter((option) => option.value);
        const feedback = search.parentElement.querySelector('.patient-search-feedback');
        let previousQuery = search.value.trim().toLocaleLowerCase();

        const filterPatients = () => {
            const query = search.value.trim().toLocaleLowerCase();
            let matches = 0;

            if (query !== previousQuery && select.value) select.value = '';

            options.forEach((option) => {
                const matched = option.textContent.toLocaleLowerCase().includes(query);
                option.hidden = Boolean(query) && !matched;
                if (matched) matches += 1;
            });

            if (feedback) {
                if (!query) {
                    feedback.textContent = `${options.length} patients available. Start typing to narrow the list.`;
                } else if (matches === 0) {
                    feedback.textContent = 'No patients match that search.';
                } else {
                    feedback.textContent = `${matches} patient${matches === 1 ? '' : 's'} found. Select one from the list below.`;
                }
            }
            previousQuery = query;
        };

        search.addEventListener('input', filterPatients);
        filterPatients();
    });
});
