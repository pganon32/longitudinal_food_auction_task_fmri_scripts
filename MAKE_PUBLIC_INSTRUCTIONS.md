# How to Make This Repository Public

This document provides step-by-step instructions for making your GitHub repository public.

## Prerequisites

Before making the repository public, ensure you have:
- [x] Reviewed all files for sensitive information
- [x] Added appropriate LICENSE file
- [x] Added .gitignore to prevent future sensitive commits
- [x] Enhanced documentation for public consumption
- [x] Added contributing guidelines

## Steps to Make Repository Public

### Method 1: Via GitHub Web Interface (Recommended)

1. **Navigate to your repository** on GitHub.com:
   https://github.com/pganon32/gut_brain_fmri_scripts

2. **Go to Settings**:
   - Click on the "Settings" tab in your repository
   - Scroll down to the "Danger Zone" section at the bottom

3. **Change visibility**:
   - Find the "Change repository visibility" section
   - Click "Change visibility"
   - Select "Make public"
   - Type your repository name to confirm
   - Click "I understand, change repository visibility"

### Method 2: Via GitHub CLI (if installed)

```bash
gh repo edit pganon32/gut_brain_fmri_scripts --visibility public
```

## Post-Publication Checklist

After making the repository public:

- [ ] Verify the repository is accessible to the public
- [ ] Check that all links in documentation work correctly
- [ ] Consider adding topics/tags to help with discoverability
- [ ] Share the repository with relevant communities
- [ ] Monitor for any security alerts from GitHub

## Important Notes

- **This action is irreversible in terms of search engines** - once public, the content may be indexed
- **Forks and stars** - Public repositories can be forked and starred by anyone
- **Issues and discussions** - Consider enabling/disabling these features as needed
- **GitHub Pages** - You can optionally enable GitHub Pages for documentation

## Security Reminders

- The .gitignore file has been configured to prevent common sensitive files
- Never commit actual research data or participant information
- Regularly review commits for accidentally added sensitive content
- Consider setting up branch protection rules if you expect contributions

## Troubleshooting

If you encounter issues:
1. Ensure you have admin permissions on the repository
2. Check that the repository doesn't violate GitHub's terms of service
3. Contact GitHub support if technical issues persist

## Repository URL After Public

Once public, your repository will be accessible at:
https://github.com/pganon32/gut_brain_fmri_scripts