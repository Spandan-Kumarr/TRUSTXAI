import { useEffect, useState, type RefObject } from 'react';

const FOCUSABLE = [
  'a[href]', 'area[href]', 'button', 'input:not([type="hidden"])',
  'select', 'textarea', 'summary', 'iframe', '[contenteditable="true"]', '[tabindex]',
].join(',');

function focusableElements(panel: HTMLElement): HTMLElement[] {
  return Array.from(panel.querySelectorAll<HTMLElement>(FOCUSABLE)).filter(element => {
    if (element.tabIndex < 0 || element.matches(':disabled') || element.closest('[inert], [hidden], [aria-hidden="true"]')) return false;
    const style = window.getComputedStyle(element);
    return style.visibility !== 'hidden' && style.visibility !== 'collapse' && element.getClientRects().length > 0;
  });
}

/** Makes a responsive drawer modal only while its mobile breakpoint matches. */
export function useDrawerFocus(
  open: boolean,
  panelRef: RefObject<HTMLElement | null>,
  breakpoint: string,
  backgroundSelectors: string[],
): boolean {
  const [matches, setMatches] = useState(() => typeof window !== 'undefined' && window.matchMedia(breakpoint).matches);
  const selectorKey = JSON.stringify(backgroundSelectors);

  useEffect(() => {
    const media = window.matchMedia(breakpoint);
    const update = () => setMatches(media.matches);
    update();
    media.addEventListener('change', update);
    return () => media.removeEventListener('change', update);
  }, [breakpoint]);

  const isModal = open && matches;

  useEffect(() => {
    const panel = panelRef.current;
    if (!isModal || !panel) return;

    const previousFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const previousTabIndex = panel.getAttribute('tabindex');
    const inertElements = new Map<HTMLElement, string | null>();

    for (const selector of JSON.parse(selectorKey) as string[]) {
      for (const element of document.querySelectorAll<HTMLElement>(selector)) {
        // An ancestor must remain interactive so that the drawer itself can receive focus.
        if (element === panel || element.contains(panel) || panel.contains(element) || inertElements.has(element)) continue;
        inertElements.set(element, element.getAttribute('inert'));
        element.inert = true;
      }
    }

    if (panel.tabIndex < 0 && previousTabIndex === null) panel.setAttribute('tabindex', '-1');
    const focusFirst = () => (focusableElements(panel)[0] ?? panel).focus({ preventScroll: true });
    focusFirst();

    const trapTab = (event: KeyboardEvent) => {
      if (event.key !== 'Tab') return;
      // Native dialogs opened from a drawer provide their own, higher-level focus trap.
      if (Array.from(document.querySelectorAll('dialog[open]')).some(dialog => !panel.contains(dialog))) return;

      const elements = focusableElements(panel);
      if (!elements.length) {
        event.preventDefault();
        panel.focus({ preventScroll: true });
        return;
      }

      const first = elements[0];
      const last = elements[elements.length - 1];
      const active = document.activeElement;
      if (!panel.contains(active) || active === panel || (event.shiftKey && active === first) || (!event.shiftKey && active === last)) {
        event.preventDefault();
        (event.shiftKey ? last : first).focus({ preventScroll: true });
      }
    };
    document.addEventListener('keydown', trapTab, true);

    return () => {
      document.removeEventListener('keydown', trapTab, true);
      for (const [element, previousInert] of inertElements) {
        if (previousInert === null) element.removeAttribute('inert');
        else element.setAttribute('inert', previousInert);
      }
      if (previousTabIndex === null) panel.removeAttribute('tabindex');
      else panel.setAttribute('tabindex', previousTabIndex);
      if (previousFocus?.isConnected && !previousFocus.closest('[inert]')) previousFocus.focus({ preventScroll: true });
    };
  }, [isModal, panelRef, selectorKey]);

  return isModal;
}
