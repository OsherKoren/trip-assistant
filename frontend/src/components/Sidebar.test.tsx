import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Sidebar } from './Sidebar';
import type { ChatSession } from '../types';

const makeSession = (id: string, title: string, updatedAt = '2026-03-21T10:00:00Z'): ChatSession => ({
  id,
  title,
  messages: [],
  createdAt: updatedAt,
  updatedAt,
});

const defaultProps = {
  sessions: [],
  activeSessionId: null,
  onNewChat: vi.fn(),
  onSelect: vi.fn(),
  onDelete: vi.fn(),
  onClose: vi.fn(),
};

describe('Sidebar', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders New Chat button', () => {
    render(<Sidebar {...defaultProps} />);
    expect(screen.getByRole('button', { name: /new chat/i })).toBeInTheDocument();
  });

  it('shows empty state when no sessions', () => {
    render(<Sidebar {...defaultProps} />);
    expect(screen.getByText(/no conversations yet/i)).toBeInTheDocument();
  });

  it('renders session titles', () => {
    const sessions = [
      makeSession('s1', 'What car did we rent?'),
      makeSession('s2', 'Flight details'),
    ];
    render(<Sidebar {...defaultProps} sessions={sessions} />);
    expect(screen.getByText('What car did we rent?')).toBeInTheDocument();
    expect(screen.getByText('Flight details')).toBeInTheDocument();
  });

  it('calls onNewChat when New Chat button is clicked', async () => {
    render(<Sidebar {...defaultProps} />);
    await userEvent.click(screen.getByRole('button', { name: /new chat/i }));
    expect(defaultProps.onNewChat).toHaveBeenCalledOnce();
  });

  it('calls onSelect with session id when a session is clicked', async () => {
    const sessions = [makeSession('s1', 'My question')];
    render(<Sidebar {...defaultProps} sessions={sessions} />);
    await userEvent.click(screen.getByText('My question'));
    expect(defaultProps.onSelect).toHaveBeenCalledWith('s1');
  });

  it('highlights the active session', () => {
    const sessions = [makeSession('s1', 'Active chat'), makeSession('s2', 'Other chat')];
    render(<Sidebar {...defaultProps} sessions={sessions} activeSessionId="s1" />);
    const active = screen.getByRole('button', { name: /delete.*Active chat/i });
    expect(active.closest('[aria-current="true"]')).toBeInTheDocument();
  });

  it('calls onDelete when delete button is clicked', async () => {
    const sessions = [makeSession('s1', 'To delete')];
    render(<Sidebar {...defaultProps} sessions={sessions} />);
    await userEvent.click(screen.getByRole('button', { name: /delete.*To delete/i }));
    expect(defaultProps.onDelete).toHaveBeenCalledWith('s1');
  });

  it('calls onClose when close button is clicked', async () => {
    render(<Sidebar {...defaultProps} />);
    await userEvent.click(screen.getByRole('button', { name: /close sidebar/i }));
    expect(defaultProps.onClose).toHaveBeenCalledOnce();
  });

  it('groups sessions under Today label', () => {
    const now = new Date().toISOString();
    const sessions = [makeSession('s1', 'Recent chat', now)];
    render(<Sidebar {...defaultProps} sessions={sessions} />);
    expect(screen.getByText('Today')).toBeInTheDocument();
  });
});
