# Common Accessibility Fix Patterns

## Button Accessible Names

### Icon Button
```tsx
// ❌ Bad
<button onClick={handleClose}>×</button>

// ✅ Good
<button onClick={handleClose} aria-label="Close">×</button>

// ✅ Best
<button onClick={handleClose}>
  <span aria-hidden="true">×</span>
  <span className="sr-only">Close</span>
</button>
```

## Image Alt Text

### Informative Image
```tsx
// ❌ Bad
<img src="/chart.png" />

// ✅ Good
<img src="/chart.png" alt="Sales growth chart showing 40% increase in Q4" />
```

### Decorative Image
```tsx
// ❌ Bad
<img src="/decoration.png" />

// ✅ Good
<img src="/decoration.png" alt="" aria-hidden="true" />
```

## Form Labels

### Explicit Label
```tsx
// ❌ Bad
<input type="email" placeholder="Email" />

// ✅ Good
<label htmlFor="email">Email</label>
<input id="email" type="email" />
```

## Color Contrast

### Text Colors
```tsx
// ❌ Bad (2.1:1)
<div style={{ color: '#999', background: '#fff' }}>Text</div>

// ✅ Good (4.6:1 - WCAG AA)
<div style={{ color: '#666', background: '#fff' }}>Text</div>

// ✅ Better (7.2:1 - WCAG AAA)
<div style={{ color: '#333', background: '#fff' }}>Text</div>
```

## Focus Indicators

### Modern Approach
```css
button {
  outline: none;
}

button:focus-visible {
  outline: 2px solid #2196F3;
  outline-offset: 2px;
}
```

## Keyboard Navigation

### Clickable Div
```tsx
// ❌ Bad
<div onClick={handleClick}>Click me</div>

// ✅ Good - Use button
<button onClick={handleClick}>Click me</button>

// ✅ Acceptable - Add keyboard support
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
>
  Click me
</div>
```

## SR-Only Utility

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```
