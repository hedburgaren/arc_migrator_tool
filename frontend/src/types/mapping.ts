/**
 * Type definitions for mapping operations
 */
import { Node, Edge } from 'reactflow';

export interface MappingResponse {
  id: number;
  project_id: number;
  source_field: string;
  target_field: string;
  transform_type: '1:1' | 'concat' | 'constant' | 'lookup' | 'split' | 'custom';
  transform_config: Record<string, any> | null;
  validation_rules: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

export interface MappingCreate {
  source_field: string;
  target_field: string;
  transform_type?: '1:1' | 'concat' | 'constant' | 'lookup' | 'split' | 'custom';
  transform_config?: Record<string, any>;
  validation_rules?: Record<string, any>;
}

export interface SchemaFieldNode {
  id: string;
  fieldName: string;
  dataType: string;
  sampleValues?: any[];
  nullCount?: number;
  uniqueCount?: number;
  side: 'source' | 'target';
  fileId: number;
}

export type MappingNode = Node<SchemaFieldNode>;
export type MappingEdge = Edge;
