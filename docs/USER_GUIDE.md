# ARC Migrator Tool - User Guide

This guide covers the complete workflow for using ARC Migrator Tool to migrate data between systems.

## Overview

ARC Migrator Tool provides a visual, step-by-step approach to data migration:

1. **Create a Project** - Define source and target systems
2. **Upload Data Files** - Import CSV/Excel files
3. **Discover Schemas** - Analyze data structure
4. **Create Mappings** - Visually connect source to target fields
5. **Preview & Validate** - Test transformations
6. **Execute Migration** - Run in preview, dry-run, or commit mode

## Getting Started

### Accessing the Application

After installation (see [Installation Guide](INSTALLATION.md)), access the UI at:
- **Local Development**: http://localhost:3000
- **Docker Deployment**: http://localhost:3000

### Dashboard

The dashboard displays all migration projects with their status:
- **Draft** - Project created but not configured
- **Mapping** - Field mappings in progress
- **Ready** - Ready for execution
- **Executing** - Migration running
- **Completed** - Migration finished successfully
- **Failed** - Migration encountered errors

## Step 1: Create a Project

### Using the Project Wizard

1. Click **New Project** on the dashboard
2. **Select Source System**:
   - CSV/Excel Files - For file-based imports
   - Zoho CRM/Books - For Zoho exports
   - Odoo - For Odoo data
   - HubSpot - For HubSpot exports
   - Shopify/WooCommerce - For e-commerce data

3. **Select Target System**:
   - Choose the destination for your migrated data
   
4. **Project Details**:
   - Enter a descriptive name
   - Add an optional description
   
5. Click **Create Project**

## Step 2: Upload Data Files

### Supported Formats

- **CSV** (`.csv`) - Comma, semicolon, tab, or pipe delimited
- **Excel** (`.xlsx`, `.xls`) - Single or multi-sheet workbooks
- **JSON** (`.json`) - Array or line-delimited format

### Upload Process

1. Navigate to your project
2. Go to the **Files** tab
3. Drag and drop files or click to browse
4. Wait for upload and analysis to complete

### File Analysis

After upload, ARC Migrator automatically detects:
- **Encoding** - UTF-8, ISO-8859-1, etc.
- **Delimiter** - For CSV files (comma, semicolon, tab)
- **Row Count** - Total data records
- **Column Count** - Number of fields
- **Data Types** - String, number, date, boolean

### Excel Multi-Sheet Support

**NEW**: Enhanced Excel file handling with multi-sheet support!

For Excel files with multiple sheets:

1. **Upload the Excel file** - All sheets are detected automatically
2. **View sheet information**:
   ```bash
   GET /api/files/{file_id}/sheets
   ```
   Returns:
   - Sheet names
   - Row and column counts per sheet
   - Sheet visibility status

3. **Select a sheet for analysis**:
   - In the Files tab, click on the uploaded Excel file
   - Click **Show Sheets** to view all available sheets
   - Select the sheet you want to analyze
   - The schema will be analyzed for the selected sheet

4. **Excel metadata**:
   - View formulas, charts, and pivot tables
   - See document properties (creator, modified date, etc.)
   - Access via `/api/files/{file_id}/excel-metadata`

**Excel Features Preserved**:
- Cell formatting (when exporting)
- Multiple data types (numbers, dates, formulas)
- Column width auto-adjustment
- Header row freezing
- Auto-filters on export

## Step 3: Discover Schemas

### Automatic Schema Discovery

1. In the **Files** tab, find your uploaded file
2. Click **Discover Schema**
3. Review the discovered fields:
   - **Field Name** - Column header
   - **Display Name** - Human-readable name
   - **Data Type** - Inferred type (string, integer, date, etc.)
   - **Required** - Fields with few null values
   - **Primary Key** - Candidate unique identifiers
   - **Lookup** - Fields with limited unique values

### Schema Types

- **Source Schema** - Structure of your input data
- **Target Schema** - Structure of your output data

### Creating Target Schemas

For file-based targets, upload a template file and discover its schema. The target schema defines the expected output format.

### Field Types

| Type | Description | Example |
|------|-------------|---------|
| string | Text data | "John Doe" |
| integer | Whole numbers | 42 |
| float | Decimal numbers | 3.14 |
| boolean | True/False | true, yes, 1 |
| date | Date values | 2024-01-15 |
| datetime | Date and time | 2024-01-15T10:30:00 |
| enum | Limited options | "Active", "Inactive" |
| lookup | Reference values | Category names |

## Step 4: Create Field Mappings

### Opening the Mapping Editor

1. Go to the **Mappings** tab
2. Click **New Mapping**
3. Click **Open Editor** to launch the visual mapping workspace

### Visual Mapping Interface

The mapping editor displays:
- **Left Side** - Source schema fields (blue)
- **Right Side** - Target schema fields (green)
- **Center** - Connection lines and transforms

### Creating Connections

1. Click on a source field handle (right side of node)
2. Drag to a target field handle (left side of node)
3. Release to create the connection

### Mapping Types

#### Direct Mapping (1:1)
Connect one source field directly to one target field.

#### Constant Value
Set a fixed value for a target field:
- Right-click target field → Set Constant
- Enter the value (e.g., "Active", "2024")

#### Concatenation (N:1)
Combine multiple source fields:
- Connect first field to target
- Configure transform as "concat"
- Add additional source fields
- Set separator (space, comma, etc.)

#### Split (1:N)
Split one field into multiple:
- Connect to first target field
- Configure split separator and index
- Repeat for other target fields

#### Lookup Transform
Map source values to target values:
- Connect source to target
- Configure lookup table
- Example: Map "M"/"F" to "Male"/"Female"

### Advanced Transform Nodes

**NEW**: Visual transform nodes for complex data transformations!

#### Lookup Transform 🔍
Map source values to target values using a lookup table.

**Use Case**: Convert codes to descriptions (e.g., "M" → "Male", "F" → "Female")

**Configuration**:
- Add source-target value pairs
- Set default value for unmapped items
- Supports unlimited mappings

#### Conditional Transform ⚡
Apply if-then-else logic to transform data.

**Use Case**: Categorize data based on conditions

**Configuration**:
- Multiple conditions with operators (==, !=, >, <, contains, etc.)
- Then-value for each condition
- Default value for unmatched conditions

**Example**:
```
If value > 100 then "High"
If value > 50 then "Medium"
Else "Low"
```

#### Math Transform 🔢
Perform mathematical operations on numeric data.

**Operations**:
- **Single field**: Add, Subtract, Multiply, Divide, Round, Absolute, Ceiling, Floor
- **Multiple fields**: Sum, Average, Min, Max

**Use Case**: Calculate totals, percentages, or apply formulas

#### Date Transform 📅
Parse, format, and manipulate dates.

**Operations**:
- Format dates (various formats supported)
- Extract year, month, day, or day of week
- Add/subtract days or months

**Use Case**: Standardize date formats, extract date components

**Common Formats**:
- YYYY-MM-DD (2024-01-15)
- DD/MM/YYYY (15/01/2024)
- MM/DD/YYYY (01/15/2024)
- Month DD, YYYY (January 15, 2024)

#### String Transform 📝
Advanced string manipulation operations.

**Operations**:
- Case conversion (lowercase, uppercase, title case)
- Trimming (trim, ltrim, rtrim)
- Find and replace
- Substring extraction
- Padding (left/right with fill character)
- Remove special characters or whitespace
- Normalize whitespace

**Use Case**: Clean and standardize text data

#### Custom Transform ⚙️
Placeholder for user-defined transformations (coming soon).

### Using Transform Nodes

1. **Add a transform node**:
   - Drag from the transform library
   - Or right-click in workspace → Add Transform

2. **Configure the transform**:
   - Click on the node
   - Click "Configure" button
   - Set parameters based on transform type

3. **Connect nodes**:
   - Connect source field → transform node
   - Connect transform node → target field
   - Chain multiple transforms if needed

4. **Test the transformation**:
   - Use Preview mode to see results
   - Adjust configuration as needed

### Available Transforms (Legacy)

| Transform | Description | Configuration |
|-----------|-------------|---------------|
| 1:1 | Direct mapping | - |
| constant | Fixed value | value |
| concat | Join fields | separator, fields |
| split | Split by delimiter | separator, index |
| lookup | Value mapping | lookup table |
| conditional | If-then-else | conditions |
| math | Calculations | operation, operand |
| date | Date operations | format, operation |
| string | String manipulation | operation |
| custom | User-defined | function code |

### Saving Mappings

Mappings are saved automatically when you:
- Create a new connection
- Modify a transform
- Delete a connection

## Step 5: Preview & Validate

### Preview Mode

1. In the mapping workspace, click **Preview**
2. View side-by-side comparison:
   - Source data (original)
   - Transformed data (result)
3. Review warnings for potential issues

### Warning Types

- **Missing Source** - Source field not found
- **Lookup Not Found** - No match in lookup table
- **Type Conversion** - Failed type conversion

### Validation Checks

The system validates:
- Required fields have values
- Data types match expectations
- String lengths within limits
- Numeric values within ranges

## Step 6: Execute Migration

### Execution Modes

#### Preview Mode
- Process first 100 rows only
- No output files created
- Quick validation of mappings

#### Dry Run Mode
- Process all records
- No output files created
- Full validation with statistics

#### Commit Mode
- Process all records
- Generate output files (CSV, Excel)
- Create audit log

### Running a Migration

1. In the mapping workspace, choose execution mode:
   - **Preview** - Quick test
   - **Dry Run** - Full validation
   - **Execute** - Commit changes

2. Monitor progress on the Execution Monitor:
   - Total records
   - Processed count
   - Success/Failure counts
   - Warnings

3. Review results:
   - Download output files
   - Review error logs
   - Check transformation results

### Output Files

Successful commit mode generates:
- **CSV File** - `project_X_profile_Y_timestamp.csv`
- **Excel File** - `project_X_profile_Y_timestamp.xlsx`

Files are stored in the configured output directory.

## Best Practices

### Before Migration

1. **Backup source data** before starting
2. **Clean source data** when possible
3. **Document field meanings** for complex schemas
4. **Test with sample data** using Preview mode

### During Mapping

1. **Start with required fields** - Map critical fields first
2. **Use meaningful names** - Rename for clarity
3. **Test transforms individually** - Preview after each change
4. **Document complex mappings** - Note business logic

### Before Commit

1. **Run Dry Run first** - Validate all records
2. **Review warnings** - Address data quality issues
3. **Check record counts** - Verify expected numbers
4. **Verify sample output** - Spot-check transformed data

### After Migration

1. **Verify output files** - Open and inspect results
2. **Import to target** - Load into destination system
3. **Validate in target** - Check data integrity
4. **Document the process** - Record for future migrations

## Troubleshooting

### Common Issues

#### "Source field not found"
- Check field names match exactly (case-sensitive)
- Verify source file was uploaded correctly
- Re-discover schema if needed

#### "Failed to parse file"
- Check file encoding (try UTF-8)
- Verify delimiter for CSV files
- Ensure file isn't corrupted

#### "No target schema"
- Upload a target template file
- Discover schema from the template
- Or create target schema manually

#### "Execution failed"
- Check execution logs for specific errors
- Review warning messages
- Verify all required mappings exist

### Getting Help

1. Check the [Architecture Guide](ARCHITECTURE.md) for technical details
2. Review execution logs for specific error messages
3. Use Preview mode to debug mapping issues
4. Check logs in `backend/data/logs/` for detailed error information

## Best Practices

### Data Preparation

1. **Clean source data before migration**:
   - Remove duplicate records
   - Fix data quality issues at the source
   - Standardize formats when possible

2. **Use consistent encoding**:
   - UTF-8 is recommended
   - Check file encoding before upload
   - Use the encoding detection feature

3. **Optimize Excel files**:
   - Remove unnecessary sheets
   - Convert formulas to values if needed
   - Keep file sizes under 100MB

### Mapping Strategy

1. **Start simple**:
   - Begin with direct 1:1 mappings
   - Add transforms gradually
   - Test each transformation

2. **Use transform nodes effectively**:
   - Chain transforms for complex logic
   - Use lookup nodes for code conversions
   - Apply conditional nodes for categorization

3. **Handle null values**:
   - Configure null handling in transforms
   - Use default values in lookup nodes
   - Test with null data in preview

### Performance Optimization

1. **Process data in batches**:
   - Split large files if possible
   - Use preview mode for testing
   - Monitor execution times

2. **Optimize mappings**:
   - Minimize nested transforms
   - Use efficient transform types
   - Test performance with large datasets

3. **Monitor resource usage**:
   - Check metrics endpoint
   - Review logs for performance issues
   - Adjust system resources if needed

### Security and Compliance

1. **Protect sensitive data**:
   - Be cautious with personally identifiable information
   - Review data before committing
   - Use secure connections in production

2. **Audit trail**:
   - Review audit logs regularly
   - Document migration processes
   - Keep backup copies of original data

3. **Rate limiting**:
   - Respect API rate limits
   - Batch operations when possible
   - Monitor rate limit headers

### Troubleshooting

1. **Schema analysis fails**:
   - Check file encoding
   - Verify file format (CSV/Excel)
   - Review file for corruption

2. **Transform errors**:
   - Check data types match operation
   - Verify source field names
   - Test with sample data

3. **Performance issues**:
   - Reduce preview row count
   - Simplify transform chains
   - Check system resources

4. **Excel issues**:
   - Select specific sheet if multiple exist
   - Convert formulas to values if needed
   - Check for hidden sheets

## Advanced Features

### Excel Export with Formatting

When exporting to Excel, the system automatically:
- Adjusts column widths
- Freezes header row
- Applies auto-filters
- Preserves data types

Customize export options:
```python
{
  "format": "xlsx",
  "options": {
    "sheet_name": "Migration Results",
    "auto_filter": true,
    "freeze_panes": "A2",
    "auto_width": true
  }
}
```

### Transform Node Chaining

Combine multiple transforms for complex logic:
```
Source Field → String (trim) → Conditional (categorize) → Lookup (map) → Target Field
```

### Custom Validation Rules

Use conditional transforms for validation:
- Check required fields
- Validate data ranges
- Ensure format compliance

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+S | Save current mapping |
| Delete | Remove selected edge |
| Ctrl+Z | Undo (where supported) |
| Ctrl+Click | Multi-select nodes |

## API Access

For programmatic access, see the API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Metrics**: http://localhost:8000/metrics
- **Health Check**: http://localhost:8000/health
