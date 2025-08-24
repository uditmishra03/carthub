# Carthub Documentation Images

This directory contains all screenshots and visual assets used in the Carthub documentation.

## Screenshot Naming Convention

All screenshots follow a consistent naming pattern for easy reference and maintenance:

### User Interface Screenshots
- `homepage-first-visit.png` - Carthub homepage for new visitors
- `account-creation.png` - Account registration form
- `profile-settings.png` - User profile management interface
- `category-navigation.png` - Category menu structure
- `search-results.png` - Search results with filters applied
- `product-details.png` - Complete product detail page

### Cart Management Screenshots
- `add-to-cart-success.png` - Successful item addition with confirmation
- `mini-cart-preview.png` - Hover-activated mini-cart
- `full-cart-page.png` - Comprehensive cart management page
- `quantity-update.png` - Quantity adjustment controls
- `item-removal.png` - Item removal with bin icon
- `persistent-cart.png` - Cart persistence demonstration
- `price-breakdown.png` - Transparent pricing with all components

### Checkout Process Screenshots
- `checkout-cart-review.png` - Cart review step in checkout
- `shipping-address.png` - Shipping address entry form
- `payment-methods.png` - Available payment options
- `order-confirmation.png` - Final order review before purchase
- `order-confirmation-page.png` - Order confirmation with details

### Order Management Screenshots
- `order-tracking.png` - Order tracking interface with status updates
- `order-history.png` - Order history page with past purchases
- `return-process.png` - Return initiation interface

### Architecture and Technical Screenshots
- `data-flow-diagram.png` - Backend data flow visualization
- `architecture-overview.png` - High-level system architecture
- `mobile-responsive.png` - Mobile device compatibility

## Image Specifications

### Technical Requirements
- **Format**: PNG (preferred) or JPG
- **Resolution**: Minimum 1920x1080 for desktop screenshots
- **Mobile Screenshots**: Actual device resolution (e.g., 375x812 for iPhone)
- **Quality**: High quality, crisp and clear
- **File Size**: Optimized for web (typically under 500KB)

### Visual Standards
- **Consistent Styling**: Use the same browser and theme for all screenshots
- **Clean Interface**: Remove personal information and use placeholder data
- **Highlighting**: Use consistent colors for callouts and annotations
- **Annotations**: Add arrows, boxes, or text to highlight important features

### Content Guidelines
- **Sample Data**: Use realistic but generic sample data
- **Privacy**: No real customer information or sensitive data
- **Branding**: Ensure Carthub branding is visible and consistent
- **Accessibility**: Consider color contrast and readability

## Screenshot Capture Guidelines

### Browser Setup
- **Browser**: Use Chrome or Firefox for consistency
- **Window Size**: 1920x1080 for desktop screenshots
- **Zoom Level**: 100% (default zoom)
- **Extensions**: Disable or hide browser extensions
- **Bookmarks**: Hide bookmark bar for cleaner appearance

### Mobile Screenshots
- **Device**: Use actual devices or high-quality emulators
- **Orientation**: Portrait for most screenshots, landscape when relevant
- **Status Bar**: Clean status bar with good signal/battery indicators
- **Gestures**: Show touch interactions when relevant

### Annotation Tools
Recommended tools for adding annotations:
- **Snagit**: Professional screenshot and annotation tool
- **Skitch**: Simple annotation tool
- **Figma**: For more complex diagrams and annotations
- **Adobe Photoshop**: For advanced editing

## Image Organization

### Directory Structure
```
images/
├── ui/                 # User interface screenshots
├── cart/              # Cart management screenshots
├── checkout/          # Checkout process screenshots
├── orders/            # Order management screenshots
├── architecture/      # Technical diagrams and architecture
├── mobile/           # Mobile-specific screenshots
└── annotations/      # Source files for annotated images
```

### File Naming Best Practices
- Use lowercase letters and hyphens
- Be descriptive but concise
- Include version numbers for updated screenshots
- Use consistent prefixes for related screenshots

## Maintenance Schedule

### Regular Updates
- **Monthly Review**: Check for outdated screenshots
- **Feature Updates**: Capture new features as they're released
- **UI Changes**: Update screenshots when interface changes
- **Quality Check**: Ensure all images meet quality standards

### Version Control
- **Git Tracking**: All images tracked in version control
- **Change Documentation**: Document reasons for image updates
- **Archive Old Versions**: Keep previous versions for reference
- **Approval Process**: Review changes before committing

## Usage in Documentation

### Markdown Integration
```markdown
![Alt text](images/screenshot-name.png)
*Caption: Description of what the screenshot shows*
```

### HTML Integration
```html
<img src="images/screenshot-name.png" alt="Alt text" />
<p><em>Caption: Description of what the screenshot shows</em></p>
```

### Responsive Images
For responsive documentation:
```html
<picture>
  <source media="(max-width: 768px)" srcset="images/mobile/screenshot-mobile.png">
  <img src="images/screenshot-desktop.png" alt="Alt text">
</picture>
```

## Accessibility Considerations

### Alt Text Guidelines
- **Descriptive**: Explain what the image shows
- **Concise**: Keep alt text under 125 characters when possible
- **Context**: Consider the surrounding text
- **Functionality**: Describe what actions are shown

### Color and Contrast
- **High Contrast**: Ensure text is readable
- **Color Independence**: Don't rely solely on color to convey information
- **Consistent Colors**: Use the same colors for similar elements

## Tools and Resources

### Screenshot Tools
- **macOS**: Built-in Screenshot app (Cmd+Shift+5)
- **Windows**: Snipping Tool or Snip & Sketch
- **Linux**: GNOME Screenshot or Spectacle
- **Browser Extensions**: Full Page Screen Capture, Awesome Screenshot

### Image Editing
- **Free**: GIMP, Paint.NET, Canva
- **Paid**: Adobe Photoshop, Sketch, Figma
- **Online**: Photopea, Canva, Remove.bg

### Optimization Tools
- **TinyPNG**: PNG compression
- **ImageOptim**: Mac image optimization
- **Squoosh**: Google's web-based image optimizer

## Contributing Images

### Submission Process
1. **Capture**: Take high-quality screenshots following guidelines
2. **Edit**: Add annotations and optimize file size
3. **Name**: Use consistent naming convention
4. **Review**: Check quality and accuracy
5. **Submit**: Create pull request with new images

### Review Criteria
- **Quality**: Clear, high-resolution images
- **Relevance**: Accurately represents current application state
- **Consistency**: Matches existing visual standards
- **Accessibility**: Includes proper alt text and descriptions

## Contact

For questions about documentation images:
- **Documentation Team**: docs@carthub.com
- **Design Team**: design@carthub.com
- **Technical Issues**: tech-support@carthub.com

---

*This image directory is maintained by the Carthub documentation team. Last updated: August 21, 2025*
