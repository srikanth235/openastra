import { Calendar, Database } from 'lucide-react';
import type { SimpleIcon } from 'simple-icons';
import {
  siGmail,
  siGithub,
  siSlack,
  siOpenai,
  siDropbox,
  siGooglecalendar,
  siMetabase,
  siIcloud,
  siCalendly,
} from 'simple-icons';

export interface IntegrationMetadata {
  id: string;
  name: string;
  description: string;
  icon: SimpleIcon;
  category:
    | 'Communication'
    | 'Development'
    | 'Analytics'
    | 'Storage'
    | 'AI'
    | 'Productivity';
  authMethods: Array<'oauth2' | 'bearer' | 'basic' | 'api_key'>;
  apiEndpointCount: number;
  docsUrl: string;
  features: string[];
  tags: string[];
}

export const integrationRegistry: Record<string, IntegrationMetadata> = {
  gmail: {
    id: 'gmail',
    name: 'Gmail',
    description: 'Connect to Gmail to send and manage emails.',
    icon: siGmail,
    category: 'Communication',
    authMethods: ['oauth2', 'bearer'],
    apiEndpointCount: 17,
    docsUrl: 'https://gmail.googleapis.com/$discovery/rest?version=v1',
    features: [
      'Send emails',
      'Read inbox',
      'Manage labels',
      'Search emails',
      'Handle attachments',
    ],
    tags: ['email', 'communication', 'google'],
  },
  github: {
    id: 'github',
    name: 'GitHub',
    description:
      'Integrate with GitHub for repository and workflow management.',
    icon: siGithub,
    category: 'Development',
    authMethods: ['oauth2', 'bearer'],
    apiEndpointCount: 324,
    docsUrl:
      'https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.json',
    features: [
      'Repository management',
      'Issue tracking',
      'Pull requests',
      'Actions workflows',
      'Team collaboration',
    ],
    tags: ['git', 'development', 'code'],
  },
  slack: {
    id: 'slack',
    name: 'Slack',
    description: 'Send messages and interact with Slack workspaces.',
    icon: siSlack,
    category: 'Communication',
    authMethods: ['oauth2', 'bearer'],
    apiEndpointCount: 125,
    docsUrl:
      'https://raw.githubusercontent.com/slackapi/slack-api-specs/master/web-api/slack_web_openapi_v2.json',
    features: [
      'Send messages',
      'Create channels',
      'Manage users',
      'File sharing',
      'Slash commands',
    ],
    tags: ['chat', 'communication', 'team'],
  },
  openai: {
    id: 'openai',
    name: 'OpenAI',
    description: 'Access GPT models and DALL-E for AI capabilities.',
    icon: siOpenai,
    category: 'AI',
    authMethods: ['bearer'],
    apiEndpointCount: 15,
    docsUrl: 'https://platform.openai.com/docs/api-reference',
    features: [
      'Text generation',
      'Image generation',
      'Embeddings',
      'Fine-tuning',
      'Moderation',
    ],
    tags: ['ai', 'ml', 'gpt'],
  },
  dropbox: {
    id: 'dropbox',
    name: 'Dropbox',
    description: 'Cloud storage and file management integration.',
    icon: siDropbox,
    category: 'Storage',
    authMethods: ['oauth2'],
    apiEndpointCount: 85,
    docsUrl: 'https://www.dropbox.com/developers/documentation',
    features: [
      'File storage',
      'File sharing',
      'Team collaboration',
      'File sync',
      'Paper docs',
    ],
    tags: ['storage', 'files', 'cloud'],
  },
  google_calendar: {
    id: 'google_calendar',
    name: 'Google Calendar',
    description: 'Manage events and schedules through Google Calendar.',
    icon: siGooglecalendar,
    category: 'Productivity',
    authMethods: ['oauth2'],
    apiEndpointCount: 42,
    docsUrl: 'https://developers.google.com/calendar',
    features: [
      'Event management',
      'Calendar sharing',
      'Meeting scheduling',
      'Reminders',
      'Resource booking',
    ],
    tags: ['calendar', 'scheduling', 'google'],
  },
};

export const categories = {
  communication: {
    name: 'Communication',
    icon: siSlack,
  },
  development: {
    name: 'Development',
    icon: siGithub,
  },
  analytics: {
    name: 'Analytics',
    icon: siMetabase,
  },
  storage: {
    name: 'Storage',
    icon: Database,
  },
  ai: {
    name: 'Artificial Intelligence',
    icon: siOpenai,
  },
  productivity: {
    name: 'Productivity',
    icon: Calendar,
  },
};

export function getIntegrationsByCategory(category: string) {
  return Object.values(integrationRegistry).filter(
    (integration) => integration.category === category,
  );
}

export function searchIntegrations(query: string) {
  const searchTerm = query.toLowerCase();
  return Object.values(integrationRegistry).filter(
    (integration) =>
      integration.name.toLowerCase().includes(searchTerm) ||
      integration.description.toLowerCase().includes(searchTerm) ||
      integration.tags.some((tag) => tag.toLowerCase().includes(searchTerm)),
  );
}

export function getAuthMethodLabel(method: string): string {
  const labels: Record<string, string> = {
    oauth2: 'OAuth 2.0',
    bearer: 'Bearer Token',
    basic: 'Basic Auth',
    api_key: 'API Key',
  };
  return labels[method] || method;
}

interface Tool {
  name: string;
  description: string;
}

export const tools: Record<string, Tool[]> = {
  gmail: [
    {
      name: 'send_email',
      description:
        'Send an email to specified recipients with subject and body content',
    },
    {
      name: 'search_emails',
      description:
        'Search through emails using specified criteria like subject, sender, or date range',
    },
    {
      name: 'manage_labels',
      description: 'Create, modify, or apply labels to organize emails',
    },
  ],
  github: [
    {
      name: 'create_issue',
      description:
        'Create a new issue in a specified repository with title and description',
    },
    {
      name: 'get_pull_requests',
      description:
        'Retrieve pull requests for a repository with optional filtering',
    },
    {
      name: 'list_repositories',
      description:
        'List repositories for a user or organization with specified criteria',
    },
  ],
  slack: [
    {
      name: 'post_message',
      description: 'Send a message to a specified channel or user',
    },
    {
      name: 'create_channel',
      description: 'Create a new channel with specified name and settings',
    },
    {
      name: 'invite_users',
      description: 'Invite users to a specified channel or workspace',
    },
  ],
  openai: [
    {
      name: 'generate_completion',
      description:
        'Generate text completion using specified model and parameters',
    },
    {
      name: 'create_image',
      description: 'Generate an image using DALL-E with specified parameters',
    },
    {
      name: 'create_embedding',
      description: 'Generate embeddings for provided text content',
    },
  ],
  dropbox: [
    {
      name: 'upload_file',
      description: 'Upload a file to a specified Dropbox path',
    },
    {
      name: 'share_file',
      description:
        'Create a sharing link for a file with specified permissions',
    },
    {
      name: 'list_folder',
      description: 'List contents of a specified folder path',
    },
  ],
  google_calendar: [
    {
      name: 'create_event',
      description:
        'Create a calendar event with specified details and attendees',
    },
    {
      name: 'list_events',
      description: 'Retrieve calendar events within a specified time range',
    },
    {
      name: 'update_event',
      description: "Modify an existing calendar event's details",
    },
  ],
};
