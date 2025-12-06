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

### Excel Sheets

For Excel files with multiple sheets:
1. Click on the uploaded file
2. Select **Show Sheets**
3. Choose the sheet to import
4. The data from that sheet will be analyzed

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

### Available Transforms

| Transform | Description | Configuration |
|-----------|-------------|---------------|
| none | No transformation | - |
| lowercase | Convert to lowercase | - |
| uppercase | Convert to uppercase | - |
| trim | Remove whitespace | - |
| concat | Join fields | separator |
| split | Split by delimiter | separator, index |
| replace | Find and replace | old, new |
| format_date | Format dates | output format |
| to_number | Convert to number | default value |
| to_string | Convert to string | - |
| lookup | Value mapping | lookup table |

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
