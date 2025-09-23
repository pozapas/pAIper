/**
 * Hydration-safe utilities for handling browser extension conflicts
 */

/**
 * Clean up browser extension attributes that can cause hydration mismatches
 */
export function cleanupBrowserExtensionAttributes(): void {
  if (typeof window === 'undefined') return;

  const html = document.documentElement;
  const body = document.body;

  // Common browser extension attributes that cause hydration issues
  const problematicAttributes = [
    'data-lt-installed',           // LanguageTool
    'data-grammarly-extension-installed', // Grammarly
    'data-new-gr-c-s-check-loaded',      // Grammarly
    'data-gr-ext-installed',             // Grammarly
    'data-darkreader-mode',              // Dark Reader
    'data-darkreader-scheme',            // Dark Reader  
    'data-vimium-hints',                 // Vimium
    'data-adblock',                      // AdBlock extensions
    'data-lastpass-icon-root',           // LastPass
  ];

  // Clean HTML element
  problematicAttributes.forEach(attr => {
    if (html.hasAttribute(attr)) {
      html.removeAttribute(attr);
    }
  });

  // Clean body element
  problematicAttributes.forEach(attr => {
    if (body?.hasAttribute(attr)) {
      body.removeAttribute(attr);
    }
  });

  // Also clean up any dynamically added classes by extensions
  const problematicClasses = [
    'gr_-check-loaded',
    'lt-installed',
    'vimium-hints',
  ];

  problematicClasses.forEach(className => {
    if (html.classList.contains(className)) {
      html.classList.remove(className);
    }
    if (body?.classList.contains(className)) {
      body.classList.remove(className);
    }
  });
}

/**
 * Initialize cleanup and monitor for changes
 */
export function initializeHydrationFixes(): void {
  if (typeof window === 'undefined') return;

  // Clean up immediately
  cleanupBrowserExtensionAttributes();

  // Clean up after DOM is loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', cleanupBrowserExtensionAttributes);
  } else {
    cleanupBrowserExtensionAttributes();
  }

  // Monitor for changes (extensions might add attributes later)
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.type === 'attributes' && 
          (mutation.target === document.documentElement || 
           mutation.target === document.body)) {
        // Debounce cleanup to avoid excessive calls
        setTimeout(cleanupBrowserExtensionAttributes, 100);
      }
    });
  });

  // Start observing
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: [
      'data-lt-installed',
      'data-grammarly-extension-installed', 
      'data-new-gr-c-s-check-loaded',
      'data-gr-ext-installed',
      'data-darkreader-mode',
      'data-darkreader-scheme',
      'class'
    ]
  });

  if (document.body) {
    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ['class', 'data-grammarly-extension-installed']
    });
  }
}