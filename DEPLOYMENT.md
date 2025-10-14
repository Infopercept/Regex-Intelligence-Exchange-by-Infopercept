# Manual Deployment Instructions

This document provides step-by-step instructions for manually deploying the Regex Intelligence Exchange by Infopercept documentation site to GitHub Pages.

## Prerequisites

1. Ensure you have the necessary permissions to deploy to the GitHub Pages site
2. Have Git installed on your local machine
3. Be familiar with the command line

## Deployment Steps

### 1. Prepare Your Changes

1. Make sure all your changes are committed to the `master` branch:
   ```bash
   git add .
   git commit -m "feat: Describe your changes here"
   git push origin master
   ```

### 2. Configure GitHub Pages (First Time Only)

1. Go to your repository on GitHub
2. Click on "Settings" tab
3. Scroll down to the "Pages" section
4. Under "Build and deployment":
   - Set "Source" to "Deploy from a branch"
   - Set "Branch" to "master" and "/docs" folder
5. Click "Save"

**Note**: The repository includes a `.nojekyll` file in the `/docs` directory to disable Jekyll processing, and the `CNAME` file has been updated to point to the correct domain.

### 3. Manual Deployment Process

Since we're using manual deployment, you'll need to follow these steps each time you want to deploy changes:

1. Ensure all changes are pushed to the `master` branch
2. Go to the GitHub repository page
3. Click on the "Actions" tab
4. If there are any workflows listed, you can manually trigger them by clicking on them and using the "Run workflow" button
5. Alternatively, you can wait for GitHub Pages to automatically detect changes in the `/docs` directory

### 4. Verify Deployment

1. After deployment, visit your site at: https://infopercept.github.io/Regex-Intelligence-Exchange-by-Infopercept/

**Note**: If you have a custom domain configured, visit that domain instead.
2. Check that your changes are visible
3. If you don't see your changes immediately, wait a few minutes and refresh

## Troubleshooting

### Common Issues

1. **Changes not appearing**: 
   - Wait 5-10 minutes for GitHub Pages to rebuild
   - Ensure your changes are actually pushed to the `master` branch
   - Check that files are in the correct `/docs` directory

2. **Permission errors**:
   - Ensure you have admin access to the repository
   - Check that GitHub Pages is properly configured in repository settings

3. **Broken links**:
   - Verify all internal links point to the correct locations
   - Check that all files are in their expected locations

## Best Practices

1. Always test your changes locally before deploying
2. Use descriptive commit messages following conventional commit format
3. Make small, incremental changes rather than large updates
4. Document significant changes in the commit message
5. Coordinate with team members to avoid conflicts

## Rollback Process

If you need to rollback to a previous version:

1. Identify the last working commit in your Git history
2. Revert to that commit:
   ```bash
   git revert <commit-hash>
   git push origin master
   ```

3. Follow the deployment steps again

## Contact

For deployment issues or questions, contact the repository maintainers.