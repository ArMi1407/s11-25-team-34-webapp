// ==========================================
//
// Description: Image handling service for Cloudinary and local storage
// Handles image URLs based on environment configuration
//
// File: apiClient.js
// Author: Anthony Bañon
// Updated: 2025-12-09
// Changes: Image URL management for Cloudinary and local storage
// ==========================================

// Environment variables
const USE_CLOUDINARY = import.meta.env.VITE_USE_CLOUDINARY === 'true';
const CLOUDINARY_CLOUD_NAME =
  import.meta.env.VITE_CLOUDINARY_CLOUD_NAME || 'dm04gis2c';
const STATIC_BASE_URL =
  import.meta.env.VITE_STATIC_URL || 'http://localhost:8000/media';
const CLOUDINARY_BASE_URL = 'https://res.cloudinary.com';

/**
 * Get the appropriate image URL based on environment configuration
 * - param {string} imagePath - The image path from API response
 * - param {Object} options - Transformation options
 * - param {number} options.width - Desired image width
 * - param {number} options.height - Desired image height
 * - param {string} options.quality - Image quality (auto, 80, 90, etc.)
 * - param {string} options.format - Image format (auto, webp, jpg, etc.)
 * - returns {string} Complete image URL
 */
export const getImageUrl = (imagePath, options = {}) => {
  const { width, height, quality = 'auto', format = 'auto' } = options;

  // Return placeholder if no image
  if (!imagePath || imagePath === '') {
    return '/placeholder.jpg';
  }

  // Cloudinary environment
  if (USE_CLOUDINARY) {
    return getCloudinaryImageUrl(imagePath, { width, height, quality, format });
  }

  // Local development environment
  return getLocalImageUrl(imagePath);
};

/**
 * Get Cloudinary image URL with transformations
 * - param {string} imagePath - Image path or Cloudinary URL
 * - param {Object} transformations - Cloudinary transformations
 * - returns {string} Cloudinary URL
 */
const getCloudinaryImageUrl = (imagePath, transformations = {}) => {
  const { width, height, quality, format } = transformations;

  // Case 1: Already a full Cloudinary URL
  if (imagePath.includes('res.cloudinary.com')) {
    return applyCloudinaryTransformations(imagePath, transformations);
  }

  // Case 2: Cloudinary public_id (stored in database)
  // Build Cloudinary URL from public_id
  let publicId = imagePath;

  // Remove /uploads prefix if present
  if (publicId.startsWith('/uploads/')) {
    publicId = publicId.substring(9); // Remove '/uploads/'
  }

  // Remove /media prefix if present
  if (publicId.startsWith('/media/')) {
    publicId = publicId.substring(7); // Remove '/media/'
  }

  // Remove file extension for Cloudinary
  publicId = publicId.replace(/\.[^/.]+$/, '');

  // Build transformations string
  let transformationStr = '';
  if (width || height) {
    transformationStr = `c_fill${width ? `,w_${width}` : ''}${
      height ? `,h_${height}` : ''
    }`;
  }
  if (quality && quality !== 'auto') {
    transformationStr += transformationStr ? `,q_${quality}` : `q_${quality}`;
  }
  if (format && format !== 'auto') {
    transformationStr += transformationStr ? `,f_${format}` : `f_${format}`;
  }

  // Add transformation separator if needed
  if (transformationStr) {
    transformationStr += '/';
  }

  // Construct Cloudinary URL
  // Format: https://res.cloudinary.com/cloud_name/image/upload/transformations/public_id
  return `${CLOUDINARY_BASE_URL}/${CLOUDINARY_CLOUD_NAME}/image/upload/${transformationStr}${publicId}`;
};

/**
 * Apply Cloudinary transformations to an existing Cloudinary URL
 * - param {string} cloudinaryUrl - Full Cloudinary URL
 * - param {Object} transformations - Transformations to apply
 * - returns {string} Transformed Cloudinary URL
 */
const applyCloudinaryTransformations = (cloudinaryUrl, transformations) => {
  const { width, height, quality, format } = transformations;

  if (!width && !height && quality === 'auto' && format === 'auto') {
    return cloudinaryUrl; // No transformations needed
  }

  try {
    const url = new URL(cloudinaryUrl);
    const pathParts = url.pathname.split('/');

    // Cloudinary URL format: /cloud_name/image/upload/[...transformations]/public_id
    // We need to insert our transformations before the public_id

    const cloudName = pathParts[1];
    let publicId = '';

    // Find where the public_id starts (after '/upload/' and any existing transformations)
    const uploadIndex = pathParts.indexOf('upload');
    if (uploadIndex !== -1) {
      // Everything after 'upload' + 1 is transformations + public_id
      // We'll reconstruct with our transformations
      const afterUpload = pathParts.slice(uploadIndex + 1);

      // The last part is the public_id (may include folders)
      publicId = afterUpload.join('/');
    }

    // Build new transformations
    let transformationStr = '';
    if (width || height) {
      transformationStr = `c_fill${width ? `,w_${width}` : ''}${
        height ? `,h_${height}` : ''
      }`;
    }
    if (quality && quality !== 'auto') {
      transformationStr += transformationStr ? `,q_${quality}` : `q_${quality}`;
    }
    if (format && format !== 'auto') {
      transformationStr += transformationStr ? `,f_${format}` : `f_${format}`;
    }

    // Reconstruct URL
    if (transformationStr) {
      return `https://res.cloudinary.com/${cloudName}/image/upload/${transformationStr}/${publicId}`;
    }

    return cloudinaryUrl;
  } catch (error) {
    console.error('Error applying Cloudinary transformations:', error);
    return cloudinaryUrl;
  }
};

/**
 * Get local image URL for development
 * - param {string} imagePath - Image path from API
 * - returns {string} Complete local image URL
 */
const getLocalImageUrl = (imagePath) => {
  // Handle different possible formats from API response

  // Case 1: Already a full URL (shouldn't happen in local, but just in case)
  if (imagePath.startsWith('http')) {
    return imagePath;
  }

  // Case 2: Path starts with /media (from Django)
  if (imagePath.startsWith('/media/')) {
    return `${STATIC_BASE_URL}${imagePath.substring(6)}`; // Remove '/media'
  }

  // Case 3: Path starts with /uploads
  if (imagePath.startsWith('/uploads/')) {
    return `${STATIC_BASE_URL}${imagePath.substring(8)}`; // Remove '/uploads'
  }

  // Case 4: Just filename or relative path
  if (
    imagePath.startsWith('products/') ||
    imagePath.startsWith('categories/')
  ) {
    return `${STATIC_BASE_URL}/${imagePath}`;
  }

  // Default: append to static base
  return `${STATIC_BASE_URL}/${imagePath}`;
};

/**
 * Generate responsive image properties for <img> tags
 * - param {string} imagePath - Image path from API
 * - param {Object} breakpoints - Screen size breakpoints
 * - returns {Object} Object with src, srcSet, and sizes properties
 */
export const getResponsiveImageProps = (imagePath, breakpoints = {}) => {
  if (!imagePath) {
    return { src: '/placeholder.jpg' };
  }

  const src = getImageUrl(imagePath);

  // If not using Cloudinary or no breakpoints, return simple src
  if (!USE_CLOUDINARY || Object.keys(breakpoints).length === 0) {
    return { src };
  }

  // Generate srcSet for Cloudinary with different sizes
  const srcSet = [];

  if (breakpoints.sm) {
    srcSet.push(
      `${getImageUrl(imagePath, { width: breakpoints.sm })} ${breakpoints.sm}w`
    );
  }
  if (breakpoints.md) {
    srcSet.push(
      `${getImageUrl(imagePath, { width: breakpoints.md })} ${breakpoints.md}w`
    );
  }
  if (breakpoints.lg) {
    srcSet.push(
      `${getImageUrl(imagePath, { width: breakpoints.lg })} ${breakpoints.lg}w`
    );
  }
  if (breakpoints.xl) {
    srcSet.push(
      `${getImageUrl(imagePath, { width: breakpoints.xl })} ${breakpoints.xl}w`
    );
  }

  return {
    src,
    srcSet: srcSet.join(', '),
    sizes:
      breakpoints.sizes ||
      '(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw',
  };
};

/**
 * Extract public_id from Cloudinary URL
 * - param {string} url - Cloudinary URL
 * - returns {string|null} Cloudinary public_id
 */
export const extractCloudinaryPublicId = (url) => {
  if (!url || !url.includes('cloudinary.com')) {
    return null;
  }

  try {
    const urlObj = new URL(url);
    const pathParts = urlObj.pathname.split('/');

    // Find index after 'upload'
    const uploadIndex = pathParts.indexOf('upload');
    if (uploadIndex !== -1 && uploadIndex + 1 < pathParts.length) {
      // Everything after 'upload' is transformations + public_id
      // Get the last segment (public_id might have transformations before it)
      // For simplicity, return everything after upload
      const publicIdParts = pathParts.slice(uploadIndex + 1);

      // If there are transformations, the public_id is everything after them
      // Cloudinary format: upload/[transformations]/public_id
      // We'll return everything after upload as the identifier
      return publicIdParts.join('/');
    }

    return null;
  } catch (error) {
    console.error('Error extracting Cloudinary public_id:', error);
    return null;
  }
};

/**
 * Check if an image URL is from Cloudinary
 * - param {string} url - Image URL to check
 * - returns {boolean} True if it's a Cloudinary URL
 */
export const isCloudinaryUrl = (url) => {
  return url && url.includes('cloudinary.com');
};

// Export as a utility object for convenience
export const imageService = {
  getImageUrl,
  getResponsiveImageProps,
  extractCloudinaryPublicId,
  isCloudinaryUrl,
};

export default imageService;
