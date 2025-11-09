# Changelog

All notable changes to AIGolos will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- API versioning (v1)
- Filtering, searching, and sorting for list views
- User statistics endpoint
- CSV export support in export_data command
- Swagger/OpenAPI documentation
- Content Security Policy (CSP) headers
- Password reset functionality
- Suspicious activity logging
- Response compression (gzip)
- Database query optimization (select_related, prefetch_related, indexes)
- Custom exceptions for better error handling
- Service layer for separation of concerns
- Django signals for automatic actions
- Management commands for data cleanup and export
- Type hints in key files
- Conversation history support in LLM

### Changed
- Improved error handling with custom exceptions
- Refactored views to use service layer
- Enhanced API documentation
- Updated README with new features
- Improved code organization and structure

### Security
- Added rate limiting for all endpoints
- Enhanced file validation (MIME type, magic bytes)
- Improved CORS configuration
- Added security headers (CSP, HSTS, etc.)
- Added logging for suspicious activity

### Performance
- Added caching support (LocMemCache with Redis option)
- Optimized database queries
- Implemented lazy loading for ML models
- Added response compression

## [2.0.0] - 2025-11-08

### Added
- Comprehensive testing infrastructure
- CI/CD with GitHub Actions
- Code coverage reporting
- Security improvements
- Performance optimizations
- Architecture improvements

### Changed
- Improved code quality and organization
- Enhanced error handling
- Better separation of concerns

## [1.0.0] - Initial Release

### Added
- ASR (Automatic Speech Recognition) using faster-whisper
- LLM (Large Language Model) integration with Ollama
- TTS (Text-to-Speech) using Piper
- User authentication and registration
- Web interface
- REST API
- Docker support
- Logging system

---

## Version History

- **v2.0.0**: Major improvements in testing, security, performance, and architecture
- **v1.0.0**: Initial release with core functionality

## Upgrade Notes

### From v1.0.0 to v2.0.0

1. **Install new dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Update environment variables** (optional):
   - Add `REDIS_URL` for caching (optional)
   - Add email settings for password reset

4. **Collect static files**:
   ```bash
   python manage.py collectstatic
   ```

5. **Review new API endpoints**:
   - `/api/v1/` - New versioned API
   - `/api/auth/api/stats/` - User statistics
   - `/api/docs/` - API documentation

## Deprecations

- Legacy API endpoints (`/api/`) are maintained for backward compatibility but will be deprecated in future versions. Use `/api/v1/` instead.

## Breaking Changes

None in v2.0.0 - all changes are backward compatible.

---

For detailed information about each release, see the [GitHub Releases](https://github.com/your-username/aigolos/releases) page.

